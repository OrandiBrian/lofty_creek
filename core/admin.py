from django.contrib import admin
from .models import Contact, ContactGroup


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'category', 'relationship_type', 'email')
    list_filter = ('category',)
    search_fields = ('name', 'phone_number', 'email')
    ordering = ('name',)
    list_per_page = 25
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'relationship_type')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'category')
        }),
    )


@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'member_count')
    search_fields = ('name',)
    filter_horizontal = ('contacts',)
    list_per_page = 25

    def member_count(self, obj):
        return obj.contacts.count()
    member_count.short_description = 'Members'
