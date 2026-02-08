from django.db import models
from django.utils import timezone

class Contact(models.Model):
    CATEGORY_CHOICES = [
        ('PARENT', 'Parent'),
        ('TEACHER', 'Teacher'),
        ('STAFF', 'Staff'),
    ]
    
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='PARENT')
    relationship_type = models.CharField(max_length=50, blank=True, null=True, help_text="E.g., Mother, Father, Guardian")
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class ContactGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="E.g., Grade 7 Parents, All Staff")
    description = models.TextField(blank=True)
    contacts = models.ManyToManyField(Contact, related_name='groups', help_text="Members of this group")
    
    def __str__(self):
        return self.name

class SMSTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    content = models.TextField(help_text="Variables allowed: {name}, {balance}, {date}, etc.")
    
    def __str__(self):
        return self.name
