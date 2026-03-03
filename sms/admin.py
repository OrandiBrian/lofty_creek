from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import SMSCampaign, SMSMessage, SMSTemplate
from .services import send_bulk_sms


@admin.register(SMSCampaign)
class SMSCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status_badge', 'message_preview', 'total_cost', 'message_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'message_body')
    filter_horizontal = ('recipients', 'recipient_groups')
    readonly_fields = ('created_at', 'updated_at', 'total_cost', 'status')
    ordering = ('-created_at',)
    list_per_page = 20
    actions = ['send_now']

    fieldsets = (
        ('Campaign Details', {
            'fields': ('name', 'message_body', 'status', 'total_cost')
        }),
        ('Recipients', {
            'fields': ('recipients', 'recipient_groups'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('scheduled_at', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colours = {
            'SENT':    '#28a745',
            'FAILED':  '#dc3545',
            'QUEUED':  '#ffc107',
            'SENDING': '#17a2b8',
            'DRAFT':   '#6c757d',
        }
        colour = colours.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            colour, obj.status
        )
    status_badge.short_description = 'Status'

    def message_preview(self, obj):
        return obj.message_body[:55] + '…' if len(obj.message_body) > 55 else obj.message_body
    message_preview.short_description = 'Message'

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Recipients'

    @admin.action(description='🚀 Send selected campaigns now')
    def send_now(self, request, queryset):
        for campaign in queryset:
            if campaign.status in ['DRAFT', 'QUEUED', 'FAILED']:
                campaign.status = 'QUEUED'
                campaign.save()
                result = send_bulk_sms(campaign)
                if 'success' in result:
                    self.message_user(request, f"✅ {campaign.name}: {result['success']}", messages.SUCCESS)
                else:
                    self.message_user(request, f"❌ {campaign.name}: {result.get('error', 'Unknown error')}", messages.ERROR)
            else:
                self.message_user(request, f"⚠️ {campaign.name} is already sent or sending.", messages.WARNING)


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ('contact', 'campaign', 'status_badge', 'cost', 'sent_at', 'delivered_at')
    list_filter = ('status', 'sent_at')
    search_fields = ('contact__name', 'contact__phone_number', 'message_body', 'at_message_id')
    readonly_fields = ('sent_at', 'at_message_id')
    ordering = ('-sent_at',)
    list_per_page = 30

    def status_badge(self, obj):
        colours = {
            'SENT':      '#28a745',
            'DELIVERED': '#007bff',
            'FAILED':    '#dc3545',
            'PENDING':   '#ffc107',
        }
        colour = colours.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            colour, obj.status
        )
    status_badge.short_description = 'Status'


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview', 'created_at')
    search_fields = ('name', 'body')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def preview(self, obj):
        return obj.body[:70] + '…' if len(obj.body) > 70 else obj.body
    preview.short_description = 'Content Preview'
