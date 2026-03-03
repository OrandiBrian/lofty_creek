from django.db import models
from core.models import Contact, ContactGroup

class SMSCampaign(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('QUEUED', 'Queued'),
        ('SENDING', 'Sending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]

    name = models.CharField(max_length=150, help_text="Internal name for this campaign")
    message_body = models.TextField()
    recipients = models.ManyToManyField(Contact, blank=True)
    recipient_groups = models.ManyToManyField(ContactGroup, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

class SMSMessage(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
    ]

    campaign = models.ForeignKey(SMSCampaign, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='sms_messages')
    message_body = models.TextField()
    at_message_id = models.CharField(max_length=100, blank=True, null=True, help_text="Africa's Talking Message ID")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"To {self.contact.phone_number} - {self.status}"

class SMSTemplate(models.Model):
    name = models.CharField(max_length=150, help_text="Template Name")
    body = models.TextField(help_text="Message body template")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
