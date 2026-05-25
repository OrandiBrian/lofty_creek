from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
from django_summernote.admin import SummernoteModelAdmin
from .models import ContactMessage, BlogPost, GalleryPhoto


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'first_name', 'last_name', 'email', 'received_at', 'is_read')
    list_filter = ('is_read', 'received_at', 'subject')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
    readonly_fields = ('received_at',)
    list_per_page = 20


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
