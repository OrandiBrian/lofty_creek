from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
import hashlib
from .models import (
    BlogPost, ContactMessage, Event, GalleryPhoto, PageImage, ResourceDocument,
    TeamMember,
)
from .forms import AdmissionInquiryForm, ContactMessageForm
from .notifications import notify_admission_inquiry, notify_contact_message

def index(request):
    today = timezone.localdate()
    gallery_photos = GalleryPhoto.objects.filter(visible=True)[:5]
    upcoming_events = Event.objects.filter(visible=True).filter(
        Q(end_date__gte=today) | Q(end_date__isnull=True, start_date__gte=today)
    ).order_by('order', 'start_date')[:3]
    return render(request, 'public/index.html', {
        'gallery_photos': gallery_photos,
        'upcoming_events': upcoming_events,
        'page_images': {
            image.slot: image
            for image in PageImage.objects.filter(slot__startswith='home_')
        },
    })

def about(request):
    team_members = TeamMember.objects.filter(visible=True)
    return render(request, 'public/about.html', {
        'team_members': team_members,
        'page_images': {
            image.slot: image
            for image in PageImage.objects.filter(slot__startswith='about_')
        },
    })

def academics(request):
    return render(request, 'public/academics.html', {
        'page_images': {
            image.slot: image
            for image in PageImage.objects.filter(slot__startswith='academics_')
        },
    })

def admissions(request):
    if request.method == 'POST':
        form = AdmissionInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            notify_admission_inquiry(inquiry)
            messages.success(
                request,
                'Your inquiry has been received. Our admissions team will contact you shortly.',
            )
            return redirect('public:admissions')
        messages.error(request, 'Please check the form and try again.')
    return render(request, 'public/admissions.html')

def gallery(request):
    photos = GalleryPhoto.objects.filter(visible=True)
    categories = ['Campus', 'Academics', 'Events', 'Sports']
    return render(request, 'public/gallery.html', {'photos': photos, 'categories': categories})

def contact(request):
    if request.method == 'POST':
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        address = forwarded.split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')
        rate_key = f"contact:{hashlib.sha256(address.encode()).hexdigest()}"
        attempts = cache.get(rate_key, 0)
        if attempts >= 5:
            return JsonResponse(
                {'status': 'error', 'message': 'Too many requests. Please try again later.'},
                status=429,
            )
        cache.set(rate_key, attempts + 1, 3600)

        form = ContactMessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            notify_contact_message(message)
            return JsonResponse({'status': 'ok'})
        return JsonResponse(
            {'status': 'error', 'message': 'Please check the form and try again.', 'errors': form.errors},
            status=400,
        )

    return render(request, 'public/contact.html')


def privacy_policy(request):
    return render(request, 'public/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'public/terms_of_service.html')


def resources(request):
    posts = BlogPost.objects.filter(published=True)
    documents = ResourceDocument.objects.filter(visible=True)
    return render(request, 'public/resources.html', {
        'posts': posts,
        'documents': documents,
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    recent = BlogPost.objects.filter(published=True).exclude(pk=post.pk)[:3]
    return render(request, 'public/blog_detail.html', {'post': post, 'recent': recent})

def events(request):
    today = timezone.localdate()
    visible_events = Event.objects.filter(visible=True)
    upcoming_events = visible_events.filter(
        Q(end_date__gte=today) | Q(end_date__isnull=True, start_date__gte=today)
    ).order_by('order', 'start_date')
    past_events = visible_events.filter(
        Q(end_date__lt=today) | Q(end_date__isnull=True, start_date__lt=today)
    ).order_by('order', '-start_date')
    return render(request, 'public/events.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    })
