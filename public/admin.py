from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from django_summernote.admin import SummernoteModelAdmin
from .models import (
    AdmissionInquiry, BlogPost, ContactMessage, Event, GalleryPhoto,
    PageImage, ResourceDocument, TeamMember,
)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'first_name', 'last_name', 'email', 'received_at', 'is_read')
    list_editable = ('is_read',)
    list_filter = ('is_read', 'received_at', 'subject')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
    readonly_fields = (
        'first_name', 'last_name', 'email', 'phone_number', 'subject',
        'message', 'received_at',
    )
    list_per_page = 20
    actions = ('mark_as_read', 'mark_as_unread')

    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        self.message_user(request, f'{queryset.update(is_read=True)} message(s) marked as read.')

    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        self.message_user(request, f'{queryset.update(is_read=False)} message(s) marked as unread.')


@admin.register(AdmissionInquiry)
class AdmissionInquiryAdmin(admin.ModelAdmin):
    list_display = ('parent_name', 'phone_number', 'grade_level', 'received_at', 'is_read')
    list_editable = ('is_read',)
    list_filter = ('is_read', 'grade_level', 'received_at')
    search_fields = ('parent_name', 'phone_number')
    readonly_fields = ('parent_name', 'phone_number', 'grade_level', 'received_at')
    date_hierarchy = 'received_at'
    list_per_page = 20
    actions = ('mark_as_read', 'mark_as_unread')

    @admin.action(description='Mark selected inquiries as read')
    def mark_as_read(self, request, queryset):
        self.message_user(request, f'{queryset.update(is_read=True)} inquiry(s) marked as read.')

    @admin.action(description='Mark selected inquiries as unread')
    def mark_as_unread(self, request, queryset):
        self.message_user(request, f'{queryset.update(is_read=False)} inquiry(s) marked as unread.')


@admin.register(ResourceDocument)
class ResourceDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'document_type', 'file_link', 'order', 'visible', 'updated_at',
    )
    list_editable = ('order', 'visible')
    list_filter = ('visible', 'document_type', 'updated_at')
    search_fields = ('title', 'description')
    readonly_fields = ('file_link', 'updated_at')
    list_per_page = 20
    fieldsets = (
        ('Download', {
            'fields': ('title', 'description', 'document_type', 'document', 'file_link'),
        }),
        ('Display settings', {
            'fields': ('order', 'visible', 'updated_at'),
        }),
    )
    actions = ('make_visible', 'make_hidden')

    @admin.display(description='Current file')
    def file_link(self, obj):
        if obj and obj.document:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">View or download file</a>',
                obj.document.url,
            )
        return 'No file uploaded'

    @admin.action(description='Show selected downloads')
    def make_visible(self, request, queryset):
        self.message_user(request, f'{queryset.update(visible=True)} download(s) made visible.')

    @admin.action(description='Hide selected downloads')
    def make_hidden(self, request, queryset):
        self.message_user(request, f'{queryset.update(visible=False)} download(s) hidden.')


@admin.register(PageImage)
class PageImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'page_location', 'updated_at')
    list_filter = ('slot',)
    readonly_fields = ('image_preview', 'updated_at')
    ordering = ('slot',)
    fieldsets = (
        ('Page location', {
            'fields': ('slot',),
            'description': 'Each location can have one managed photo. Existing website images remain as fallbacks until a photo is uploaded.',
        }),
        ('Photo', {
            'fields': ('image', 'image_preview', 'alt_text'),
        }),
        ('Last update', {
            'fields': ('updated_at',),
        }),
    )

    @admin.display(description='Location', ordering='slot')
    def page_location(self, obj):
        return obj.get_slot_display()

    @admin.display(description='Photo')
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="height:55px;width:80px;'
                'object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return '—'

    @admin.display(description='Current photo')
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" alt="" style="max-height:320px;max-width:100%;'
                'object-fit:contain;border-radius:10px;margin-top:8px;" />',
                obj.image.url,
            )
        return 'Upload a photo to see its preview.'


@admin.register(BlogPost)
class BlogPostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display  = ('title', 'category', 'author', 'published', 'cover_preview', 'created_at')
    list_filter   = ('published', 'category')
    search_fields = ('title', 'author', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('cover_preview', 'created_at', 'updated_at')
    list_editable = ('published',)
    list_per_page = 20
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'category', 'author', 'excerpt', 'content')
        }),
        ('Cover Image', {
            'fields': ('cover_image', 'cover_preview')
        }),
        ('Publishing', {
            'fields': ('published', 'created_at', 'updated_at')
        }),
    )
    actions = ['publish_posts', 'unpublish_posts']

    @admin.display(description='Cover')
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="height:60px;border-radius:6px;object-fit:cover;" />', obj.cover_image.url)
        return '—'

    @admin.action(description='✅ Publish selected posts')
    def publish_posts(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, f'{updated} post(s) published.')

    @admin.action(description='🚫 Unpublish selected posts')
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, f'{updated} post(s) unpublished.')


# ── Multi-upload form ──────────────────────────────────────────────────────────
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class BulkPhotoUploadForm(forms.Form):
    images   = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'}),
        label='Select photos (hold Ctrl / Cmd to pick multiple)',
    )
    category = forms.ChoiceField(choices=GalleryPhoto.CATEGORY_CHOICES, initial='campus')
    visible  = forms.BooleanField(required=False, initial=True, label='Make visible immediately')


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display  = ('thumbnail', 'title', 'category', 'order', 'visible', 'uploaded_at')
    list_filter   = ('category', 'visible')
    search_fields = ('title', 'description')
    list_editable = ('order', 'visible')
    list_per_page = 20
    readonly_fields = ('thumbnail_large', 'uploaded_at')
    fieldsets = (
        ('Photo', {
            'fields': ('image', 'thumbnail_large', 'title', 'description')
        }),
        ('Settings', {
            'fields': ('category', 'order', 'visible', 'uploaded_at')
        }),
    )
    actions = ['make_visible', 'make_hidden']

    # ── Inject "Upload Multiple" button into the change-list toolbar ──────────
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['bulk_upload_url'] = 'bulk_upload/'
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('bulk_upload/', self.admin_site.admin_view(self.bulk_upload_view), name='gallery_bulk_upload'),
        ]
        return custom + urls

    def bulk_upload_view(self, request):
        """Custom admin page: upload multiple photos at once."""
        if request.method == 'POST':
            form = BulkPhotoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                files    = request.FILES.getlist('images')
                category = form.cleaned_data['category']
                visible  = form.cleaned_data['visible']
                count    = 0
                for f in files:
                    # Use the filename (without extension) as a default title
                    name = f.name.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
                    GalleryPhoto.objects.create(
                        image=f,
                        title=name,
                        category=category,
                        visible=visible,
                    )
                    count += 1
                messages.success(request, f'✅ {count} photo(s) uploaded successfully.')
                return redirect('admin:public_galleryphoto_changelist')
        else:
            form = BulkPhotoUploadForm(initial={'visible': True})

        context = {
            **self.admin_site.each_context(request),
            'form': form,
            'title': 'Upload Multiple Photos',
            'opts': self.model._meta,
        }
        return render(request, 'admin/public/galleryphoto/bulk_upload.html', context)

    # ── List-view helpers ─────────────────────────────────────────────────────
    @admin.display(description='Preview')
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;width:70px;object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return '—'

    @admin.display(description='Image Preview')
    def thumbnail_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:300px;border-radius:10px;margin-top:8px;" />',
                obj.image.url
            )
        return '—'

    @admin.action(description='👁 Show selected photos')
    def make_visible(self, request, queryset):
        updated = queryset.update(visible=True)
        self.message_user(request, f'{updated} photo(s) made visible.')

    @admin.action(description='🙈 Hide selected photos')
    def make_hidden(self, request, queryset):
        updated = queryset.update(visible=False)
        self.message_user(request, f'{updated} photo(s) hidden.')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'role', 'order', 'visible')
    list_editable = ('order', 'visible')
    list_filter = ('visible',)
    search_fields = ('name', 'role', 'bio')
    readonly_fields = ('photo_preview',)
    list_per_page = 20
    fieldsets = (
        ('Team member', {
            'fields': ('name', 'role', 'bio'),
        }),
        ('Photo', {
            'fields': ('photo', 'photo_preview'),
        }),
        ('Display settings', {
            'fields': ('order', 'visible'),
        }),
    )
    actions = ('make_visible', 'make_hidden')

    @admin.display(description='Photo')
    def thumbnail(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" alt="" style="height:50px;width:50px;'
                'object-fit:cover;border-radius:50%;" />',
                obj.photo.url,
            )
        return '—'

    @admin.display(description='Current photo')
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" alt="" style="height:180px;width:180px;'
                'object-fit:cover;border-radius:50%;margin-top:8px;" />',
                obj.photo.url,
            )
        return 'No photo uploaded'

    @admin.action(description='Show selected team members')
    def make_visible(self, request, queryset):
        updated = queryset.update(visible=True)
        self.message_user(request, f'{updated} team member(s) made visible.')

    @admin.action(description='Hide selected team members')
    def make_hidden(self, request, queryset):
        updated = queryset.update(visible=False)
        self.message_user(request, f'{updated} team member(s) hidden.')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail', 'title', 'category', 'start_date', 'end_date',
        'event_status', 'order', 'visible',
    )
    list_editable = ('order', 'visible')
    list_filter = ('visible', 'category', 'start_date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_date'
    readonly_fields = ('image_preview', 'event_status')
    list_per_page = 20
    fieldsets = (
        ('Event details', {
            'fields': ('title', 'category', 'description', 'location'),
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'event_status'),
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
        }),
        ('Display settings', {
            'fields': ('order', 'visible'),
        }),
    )
    actions = ('make_visible', 'make_hidden')

    @admin.display(description='Image')
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="height:50px;width:70px;'
                'object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return '—'

    @admin.display(description='Current image')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="max-height:300px;'
                'border-radius:10px;margin-top:8px;" />',
                obj.image.url,
            )
        return 'No image uploaded'

    @admin.display(description='Page section')
    def event_status(self, obj):
        if not obj or not obj.start_date:
            return 'Upcoming Events'
        today = timezone.localdate()
        finish = obj.end_date or obj.start_date
        return 'Past Highlights' if finish < today else 'Upcoming Events'

    @admin.action(description='Show selected events')
    def make_visible(self, request, queryset):
        updated = queryset.update(visible=True)
        self.message_user(request, f'{updated} event(s) made visible.')

    @admin.action(description='Hide selected events')
    def make_hidden(self, request, queryset):
        updated = queryset.update(visible=False)
        self.message_user(request, f'{updated} event(s) hidden.')
