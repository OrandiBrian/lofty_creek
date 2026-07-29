from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
import bleach

from core.validators import validate_document_size, validate_image_size

class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    received_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.first_name} {self.last_name}"


class AdmissionInquiry(models.Model):
    GRADE_CHOICES = [
        ('ecde', 'Playgroup / PP1 / PP2 (ECDE)'),
        ('lower-primary', 'Lower Primary (G1-3)'),
        ('upper-primary', 'Upper Primary (G4-6)'),
    ]

    parent_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    grade_level = models.CharField(max_length=30, choices=GRADE_CHOICES)
    received_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-received_at']
        verbose_name_plural = 'Admission inquiries'

    def __str__(self):
        return f"{self.parent_name} — {self.get_grade_level_display()}"


class ResourceDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'PDF document'),
        ('form', 'Form'),
        ('guide', 'Guide'),
        ('other', 'Other document'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True)
    document = models.FileField(
        upload_to='resources/',
        validators=[validate_document_size],
        help_text='Upload a document up to 10 MB',
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='pdf',
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first',
    )
    visible = models.BooleanField(
        default=True,
        help_text='Uncheck to hide this download from the Resources page',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class PageImage(models.Model):
    SLOT_CHOICES = [
        ('home_hero', 'Home — Hero image'),
        ('home_about_1', 'Home — About our school image 1'),
        ('home_about_2', 'Home — About our school image 2'),
        ('home_about_3', 'Home — About our school image 3'),
        ('home_about_4', 'Home — About our school image 4'),
        ('about_story', 'About — Our story'),
        ('about_activity_1', 'About — Outdoors & activities: Various Classes'),
        ('about_activity_2', 'About — Outdoors & activities: Environment'),
        ('about_activity_3', 'About — Outdoors & activities: Gardening'),
        ('about_activity_4', 'About — Outdoors & activities: Music'),
        ('about_activity_5', 'About — Outdoors & activities: Foreign Languages'),
        ('about_activity_6', 'About — Outdoors & activities: Fitness'),
        ('academics_approach', 'Academics — Our approach'),
        ('academics_support', 'Academics — Student support'),
    ]

    slot = models.CharField(
        max_length=40,
        choices=SLOT_CHOICES,
        unique=True,
        help_text='Choose the exact page location where this photo should appear.',
    )
    image = models.ImageField(
        upload_to='page-images/',
        validators=[validate_image_size],
        help_text='Recommended size: at least 1200×800 px (maximum 5 MB).',
    )
    alt_text = models.CharField(
        max_length=180,
        blank=True,
        help_text='Optional image description for accessibility.',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['slot']
        verbose_name = 'Page image'
        verbose_name_plural = 'Page images'

    def __str__(self):
        return self.get_slot_display()


class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('Academics',     'Academics'),
        ('Activities',    'Activities'),
        ('Events',        'Events'),
        ('Announcements', 'Announcements'),
        ('Faith',         'Faith & Values'),
        ('Other',         'Other'),
    ]

    title       = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=220, unique=True, blank=True)
    category    = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Other')
    excerpt     = models.TextField(max_length=500, help_text="Short summary shown on the cards (max 500 chars)")
    content     = models.TextField(help_text="Full article content. HTML is supported.")
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True,
                                    validators=[validate_image_size],
                                    help_text="Recommended size: 800×500 px")
    author      = models.CharField(max_length=100, default='LCCS Staff')
    published   = models.BooleanField(default=False, help_text="Tick to make this post visible on the website")
    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.content = bleach.clean(
            self.content,
            tags={
                'p', 'br', 'strong', 'em', 'u', 's', 'h1', 'h2', 'h3', 'h4',
                'ul', 'ol', 'li', 'blockquote', 'a', 'img', 'table', 'thead',
                'tbody', 'tr', 'th', 'td', 'hr', 'pre', 'code',
            },
            attributes={
                'a': ['href', 'title', 'target', 'rel'],
                'img': ['src', 'alt', 'title', 'width', 'height'],
                '*': ['class'],
            },
            protocols={'http', 'https', 'mailto'},
            strip=True,
        )
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

class GalleryPhoto(models.Model):
    CATEGORY_CHOICES = [
        ('all',       'All'),
        ('campus',    'Campus'),
        ('academics', 'Academics'),
        ('events',    'Events'),
        ('sports',    'Sports'),
    ]

    image       = models.ImageField(upload_to='gallery/', validators=[validate_image_size])
    title       = models.CharField(max_length=150)
    description = models.CharField(max_length=300, blank=True)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='campus')
    order       = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first")
    visible     = models.BooleanField(default=True, help_text="Uncheck to hide from the gallery")
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=150,
        help_text="Position or responsibility shown beneath the member's name",
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="A short introduction shown on the About page",
    )
    photo = models.ImageField(
        upload_to='team/',
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text="Upload a square portrait for the best result (maximum 5 MB)",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first",
    )
    visible = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this member from the About page",
    )

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('culture', 'Culture & Arts'),
        ('community', 'Community'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='community',
    )
    image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text="Recommended size: 800×500 px (maximum 5 MB)",
    )
    legacy_image_url = models.URLField(blank=True, editable=False)
    start_date = models.DateField()
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="When set, the event moves to Past Highlights after this date",
    )
    location = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first within upcoming or past events",
    )
    visible = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this event from the Events page",
    )

    class Meta:
        ordering = ['order', 'start_date']

    def clean(self):
        super().clean()
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'The end date cannot be before the start date.',
            })

    def __str__(self):
        return self.title
