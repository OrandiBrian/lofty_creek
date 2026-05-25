from django.db import models
from django.utils import timezone
from django.utils.text import slugify

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
                                    help_text="Recommended size: 800×500 px")
    author      = models.CharField(max_length=100, default='LCCS Staff')
    published   = models.BooleanField(default=False, help_text="Tick to make this post visible on the website")
    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
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

    image       = models.ImageField(upload_to='gallery/')
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


