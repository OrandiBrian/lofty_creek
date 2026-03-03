from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from .models import SMSCampaign, SMSMessage, SMSTemplate
from core.models import Contact, ContactGroup
from .services import send_bulk_sms, SMS
import openpyxl

from django.db.models import Sum


def sms_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('sms:overview')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('sms:overview')
            else:
                messages.error(request, "You don't have permission to access the SMS dashboard.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'sms/login.html')


def sms_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('sms:login')

@staff_member_required
def dashboard_overview(request):
    total_contacts = Contact.objects.count()
    parent_count = Contact.objects.filter(category='PARENT').count()
    staff_count = Contact.objects.filter(category='STAFF').count()
    
    total_campaigns = SMSCampaign.objects.count()
    total_messages_sent = SMSMessage.objects.filter(status='SENT').count()
    total_spend = SMSMessage.objects.filter(status='SENT').aggregate(total=Sum('cost'))['total'] or 0.00
    total_templates = SMSTemplate.objects.count()
    
    recent_campaigns = SMSCampaign.objects.order_by('-created_at')[:5]
    
    context = {
        'total_contacts': total_contacts,
        'parent_count': parent_count,
        'staff_count': staff_count,
        'total_campaigns': total_campaigns,
        'total_messages_sent': total_messages_sent,
        'total_spend': total_spend,
        'total_templates': total_templates,
        'recent_campaigns': recent_campaigns,
    }
    return render(request, 'sms/overview.html', context)

@staff_member_required
def compose_sms(request):
    if request.method == 'POST':
        campaign_name = request.POST.get('campaign_name')
        message_body = request.POST.get('message_body')
        
        target_categories = request.POST.getlist('target_categories')
        target_groups = request.POST.getlist('target_groups')
        target_contacts = request.POST.getlist('target_contacts')
        
        if not campaign_name or not message_body:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": "Please provide a campaign name and message."})
            messages.error(request, "Please provide a campaign name and message.")
            return redirect('sms:compose')

        if not target_categories and not target_groups and not target_contacts:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": "Please select at least one recipient (Category, Group, or Individual Contact)."})
            messages.error(request, "Please select at least one recipient (Category, Group, or Individual Contact).")
            return redirect('sms:compose')
            
        # Create campaign
        campaign = SMSCampaign.objects.create(
            name=campaign_name,
            message_body=message_body,
            status='QUEUED'
        )
        
        # Resolve target categories to contacts
        category_contacts = Contact.objects.filter(category__in=target_categories)
        if category_contacts.exists():
            campaign.recipients.add(*list(category_contacts))
            
        # Add selected individual contacts
        if target_contacts:
            campaign.recipients.add(*target_contacts)
            
        # Add selected contact groups
        if target_groups:
            campaign.recipient_groups.add(*target_groups)

        # Trigger send
        result = send_bulk_sms(campaign)
        
        if "success" in result:
            msg_text = f"Campaign '{campaign_name}' processed! {result['success']}"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": msg_text})
            messages.success(request, msg_text)
        else:
            msg_text = f"Campaign failed: {result.get('error', 'Unknown error')}"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": msg_text})
            messages.error(request, msg_text)
            
        return redirect('sms:compose')
        
    # GET Request context
    contacts = Contact.objects.all().order_by('name')
    groups = ContactGroup.objects.all().order_by('name')
    campaigns = SMSCampaign.objects.all().order_by('-created_at')[:10]
    templates = SMSTemplate.objects.all()
    
    total_sent = SMSMessage.objects.filter(status='SENT').count()
    total_failed = SMSMessage.objects.filter(status='FAILED').count()
    campaign_count = SMSCampaign.objects.count()
    
    context = {
        'contacts': contacts,
        'groups': groups,
        'campaigns': campaigns,
        'templates': templates,
        'total_sent': total_sent,
        'total_failed': total_failed,
        'campaign_count': campaign_count
    }
        
    return render(request, 'sms/compose.html', context)

@staff_member_required
def manage_contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        category = request.POST.get('category')
        
        if not name or not phone_number or not category:
            messages.error(request, "All fields are required to add a contact.")
            return redirect('sms:contacts')
            
        try:
            # Basic formatting
            if phone_number.startswith('0'):
                phone_number = '+254' + phone_number[1:]
                
            Contact.objects.create(
                name=name,
                phone_number=phone_number,
                category=category
            )
            messages.success(request, f"Contact {name} added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding contact. Phone numbers must be unique. ({str(e)})")
            
        return redirect('sms:contacts')
        
    contacts = Contact.objects.all().order_by('-id')
    return render(request, 'sms/contacts.html', {'contacts': contacts})

@staff_member_required
def delete_contact(request, contact_id):
    if request.method == 'POST':
        try:
            contact = Contact.objects.get(id=contact_id)
            name = contact.name
            contact.delete()
            messages.success(request, f"Contact {name} was permanently removed.")
        except Contact.DoesNotExist:
            messages.error(request, "Contact not found.")
            
    return redirect('sms:contacts')

@staff_member_required
def upload_contacts(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        # Check if file has a valid extension
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, "Invalid file format. Please upload an Excel file (.xlsx or .xls).")
            return redirect('sms:contacts')
            
        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            added_count = 0
            skipped_count = 0
            
            # Assuming first row is headers: Name, Phone, Category
            # Iterate through rows starting from row 2
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row or len(row) < 2:
                    continue
                    
                name = str(row[0]).strip() if row[0] else None
                phone = str(row[1]).strip() if row[1] else None
                category = str(row[2]).strip().upper() if len(row) > 2 and row[2] else 'PARENT'
                
                # Default validation
                if not name or not phone:
                    skipped_count += 1
                    continue
                    
                if phone.startswith('0'):
                    phone = '+254' + phone[1:]
                    
                # Standardize category
                valid_categories = ['PARENT', 'TEACHER', 'STAFF']
                if category not in valid_categories:
                    category = 'PARENT'
                    
                # Create if it doesn't exist
                if not Contact.objects.filter(phone_number=phone).exists():
                    Contact.objects.create(name=name, phone_number=phone, category=category)
                    added_count += 1
                else:
                    skipped_count += 1

            if added_count > 0:
                messages.success(request, f"Successfully uploaded {added_count} contacts! (Skipped {skipped_count} existing/invalid rows)")
            else:
                messages.warning(request, f"No new contacts added. All found rows were likely duplicates or invalid. (Skipped {skipped_count})")
                
        except Exception as e:
            messages.error(request, f"Error parsing excel file: {str(e)}")
            
    return redirect('sms:contacts')

@staff_member_required
def resend_campaign(request, campaign_id):
    if request.method == 'POST':
        try:
            original = SMSCampaign.objects.get(id=campaign_id)
            new_campaign = SMSCampaign.objects.create(
                name=f"{original.name} (Resend)",
                message_body=original.message_body,
                status='QUEUED'
            )
            # Copy targeting
            new_campaign.recipients.set(original.recipients.all())
            new_campaign.recipient_groups.set(original.recipient_groups.all())
            
            # Send
            result = send_bulk_sms(new_campaign)
            
            if "success" in result:
                messages.success(request, f"Campaign resent successfully! {result['success']}")
            else:
                messages.error(request, f"Resend failed: {result.get('error', 'Unknown error')}")
                
        except SMSCampaign.DoesNotExist:
            messages.error(request, "Campaign not found.")
            
    return redirect(request.META.get('HTTP_REFERER', 'sms:overview'))

@staff_member_required
def delete_campaign(request, campaign_id):
    if request.method == 'POST':
        try:
            campaign = SMSCampaign.objects.get(id=campaign_id)
            name = campaign.name
            campaign.delete()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True})
                
            messages.success(request, f"Campaign '{name}' was deleted successfully.")
        except SMSCampaign.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": "Not found"}, status=404)
            messages.error(request, "Campaign not found.")
            
    return redirect(request.META.get('HTTP_REFERER', 'sms:overview'))

@staff_member_required
@require_POST
def resend_message(request, message_id):
    try:
        msg = SMSMessage.objects.get(id=message_id)
        
        sms = SMS()
        if not sms.api_key:
            messages.error(request, "Africa's Talking API key is missing.")
            return redirect(request.META.get('HTTP_REFERER', 'sms:compose'))
            
        recipients = [msg.contact.phone_number]
        
        try:
            if sms.sender_id:
                response = sms.sms.send(msg.message_body, recipients, sms.sender_id)
            else:
                response = sms.sms.send(msg.message_body, recipients)
                
            if 'SMSMessageData' in response and 'Recipients' in response['SMSMessageData']:
                recipient_data = response['SMSMessageData']['Recipients'][0]
                status = recipient_data.get('status')
                at_id = recipient_data.get('messageId')
                
                msg.status = 'SENT' if status == 'Success' else 'FAILED'
                msg.at_message_id = at_id
                
                cost_str = recipient_data.get('cost', '0')
                cost_val = float(cost_str.split(' ')[-1]) if ' ' in cost_str else 0.0
                msg.cost = cost_val
                
                msg.save()
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"success": True, "status": status})
                    
                messages.success(request, f"Message resent! Status: {status}")
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"success": False, "error": "Failed to parse API response."})
                messages.error(request, "Failed to parse Africa's Talking API response.")
                
        except Exception as e:
            msg.status = 'FAILED'
            msg.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "error": str(e)})
            messages.error(request, f"Error resending: {e}")
            
    except SMSMessage.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "Message not found."})
        messages.error(request, "Message not found.")
        
    return redirect(request.META.get('HTTP_REFERER', 'sms:compose'))

@staff_member_required
def manage_templates(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        body = request.POST.get('body')
        
        if not name or not body:
            messages.error(request, "Name and body are required for a template.")
        else:
            SMSTemplate.objects.create(name=name, body=body)
            messages.success(request, f"Template '{name}' created successfully.")
            
        return redirect('sms:templates')
        
    templates_list = SMSTemplate.objects.all().order_by('-created_at')
    return render(request, 'sms/templates.html', {'templates': templates_list})

@staff_member_required
def delete_template(request, template_id):
    if request.method == 'POST':
        try:
            template = SMSTemplate.objects.get(id=template_id)
            name = template.name
            template.delete()
            messages.success(request, f"Template '{name}' was deleted.")
        except SMSTemplate.DoesNotExist:
            messages.error(request, "Template not found.")
            
    return redirect('sms:templates')

@csrf_exempt
def delivery_report(request):
    """
    Webhook endpoint to receive delivery reports from Africa's Talking.
    AT expects a 200 OK response.
    """
    if request.method == 'POST':
        # Africa's Talking sends these parameters
        message_id = request.POST.get('id')
        status = request.POST.get('status')
        # failure_reason = request.POST.get('failureReason')
        
        if message_id and status:
            try:
                # Find the message recorded by services.py
                msg = SMSMessage.objects.get(at_message_id=message_id)
                
                # Check Africa's Talking statuses and map to our internal ones
                if status == 'Success':
                    msg.status = 'SENT'
                elif status == 'Delivered':
                    msg.status = 'DELIVERED'
                    msg.delivered_at = timezone.now()
                elif status in ['Failed', 'Rejected']:
                    msg.status = 'FAILED'
                
                msg.save()
            except SMSMessage.DoesNotExist:
                # Message not found or a test payload
                pass
                
    # Always respond with 200 OK so AT knows we received it
    return HttpResponse('OK', status=200)
