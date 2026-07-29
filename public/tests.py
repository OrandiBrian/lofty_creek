from datetime import timedelta

from django.test import TestCase, Client, override_settings
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from .models import (
    AdmissionInquiry, BlogPost, ContactMessage, Event, GalleryPhoto, PageImage,
    ResourceDocument, TeamMember,
)

class PublicViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        today = timezone.localdate()
        shown_photo = GalleryPhoto.objects.create(
            image='gallery/shown.jpg', title='Homepage Gallery Photo', order=1,
        )
        GalleryPhoto.objects.create(
            image='gallery/hidden.jpg', title='Hidden Gallery Photo', visible=False,
        )
        shown_event = Event.objects.create(
            title='Homepage Upcoming Event',
            description='Shown on the homepage',
            start_date=today + timedelta(days=1),
        )
        Event.objects.create(
            title='Homepage Past Event',
            description='Not shown on the homepage',
            start_date=today - timedelta(days=1),
        )
        response = self.client.get(reverse('public:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/index.html')
        self.assertContains(response, shown_photo.title)
        self.assertNotContains(response, 'Hidden Gallery Photo')
        self.assertContains(response, shown_event.title)
        self.assertNotContains(response, 'Homepage Past Event')

    def test_favicon_redirects_to_static_logo(self):
        response = self.client.get('/favicon.ico')
        self.assertRedirects(
            response,
            '/static/img/logo_2.png',
            status_code=301,
            fetch_redirect_response=False,
        )

    def test_index_uses_admin_managed_page_images(self):
        PageImage.objects.create(
            slot='home_hero',
            image='page-images/custom-home-hero.jpg',
            alt_text='Custom home hero',
        )
        response = self.client.get(reverse('public:index'))
        self.assertContains(response, '/media/page-images/custom-home-hero.jpg')
        self.assertContains(response, 'alt="Custom home hero"')

    def test_public_pages_do_not_render_placeholder_links(self):
        for route_name in (
            'index', 'about', 'academics', 'admissions', 'events', 'gallery',
            'resources', 'contact',
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(f'public:{route_name}'))
                self.assertNotContains(response, 'href="#"')

    @override_settings(
        FACEBOOK_URL='https://facebook.example/lofty-creek',
        PRIVACY_POLICY_URL='/privacy/',
    )
    def test_configured_social_and_legal_links_are_rendered(self):
        response = self.client.get(reverse('public:index'))
        self.assertContains(response, 'https://facebook.example/lofty-creek')
        self.assertContains(response, 'href="/privacy/"')

    def test_about_view(self):
        TeamMember.objects.create(name='Second Member', role='Teacher', order=20)
        TeamMember.objects.create(name='First Member', role='Director', order=10)
        TeamMember.objects.create(
            name='Hidden Member', role='Administrator', order=0, visible=False,
        )
        response = self.client.get(reverse('public:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/about.html')
        self.assertContains(response, 'First Member')
        self.assertContains(response, 'Second Member')
        self.assertNotContains(response, 'Hidden Member')
        self.assertLess(
            response.content.index(b'First Member'),
            response.content.index(b'Second Member'),
        )

    def test_about_uses_admin_managed_page_images(self):
        PageImage.objects.create(
            slot='about_activity_4',
            image='page-images/custom-music.jpg',
            alt_text='Students making music',
        )
        response = self.client.get(reverse('public:about'))
        self.assertContains(response, '/media/page-images/custom-music.jpg')
        self.assertContains(response, 'alt="Students making music"')

    def test_academics_view(self):
        response = self.client.get(reverse('public:academics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/academics.html')

    def test_academics_uses_admin_managed_page_images(self):
        PageImage.objects.create(
            slot='academics_support',
            image='page-images/custom-support.jpg',
            alt_text='Teacher supporting learners',
        )
        response = self.client.get(reverse('public:academics'))
        self.assertContains(response, '/media/page-images/custom-support.jpg')
        self.assertContains(response, 'alt="Teacher supporting learners"')

    def test_admissions_view(self):
        response = self.client.get(reverse('public:admissions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/admissions.html')

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        INQUIRY_NOTIFICATION_EMAIL='info@loftycreekchristianschool.org',
    )
    def test_admissions_inquiry_is_saved_for_admin(self):
        response = self.client.post(reverse('public:admissions'), {
            'parent_name': 'Test Parent',
            'phone_number': '0712 345 678',
            'grade_level': 'lower-primary',
            'website': '',
        })
        self.assertRedirects(response, reverse('public:admissions'))
        inquiry = AdmissionInquiry.objects.get()
        self.assertEqual(inquiry.parent_name, 'Test Parent')
        self.assertEqual(inquiry.phone_number, '+254712345678')
        self.assertEqual(inquiry.grade_level, 'lower-primary')
        self.assertFalse(inquiry.is_read)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            ['info@loftycreekchristianschool.org'],
        )
        self.assertIn('Test Parent', mail.outbox[0].body)

    def test_admissions_honeypot_rejects_bots(self):
        response = self.client.post(reverse('public:admissions'), {
            'parent_name': 'Bot',
            'phone_number': '0712345678',
            'grade_level': 'ecde',
            'website': 'https://spam.example',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(AdmissionInquiry.objects.exists())

    def test_gallery_view(self):
        response = self.client.get(reverse('public:gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/gallery.html')

    def test_contact_view(self):
        response = self.client.get(reverse('public:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/contact.html')

    def test_privacy_policy_view(self):
        response = self.client.get(reverse('public:privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/privacy_policy.html')
        self.assertContains(response, 'Children’s information and images')

    def test_terms_of_service_view(self):
        response = self.client.get(reverse('public:terms_of_service'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/terms_of_service.html')
        self.assertContains(response, 'Admissions and enquiries')

    def test_resources_view(self):
        ResourceDocument.objects.create(
            title='Visible Download',
            description='Available to parents',
            document='resources/visible.pdf',
            order=1,
        )
        ResourceDocument.objects.create(
            title='Hidden Download',
            document='resources/hidden.pdf',
            visible=False,
        )
        response = self.client.get(reverse('public:resources'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/resources.html')
        self.assertContains(response, 'Visible Download')
        self.assertNotContains(response, 'Hidden Download')

    def test_events_view(self):
        today = timezone.localdate()
        Event.objects.create(
            title='Future Event',
            description='An upcoming event',
            start_date=today + timedelta(days=7),
        )
        Event.objects.create(
            title='Current Event',
            description='An event currently in progress',
            start_date=today - timedelta(days=1),
            end_date=today,
        )
        Event.objects.create(
            title='Past Event',
            description='A completed event',
            start_date=today - timedelta(days=2),
            end_date=today - timedelta(days=1),
        )
        Event.objects.create(
            title='Hidden Event',
            description='A hidden event',
            start_date=today + timedelta(days=1),
            visible=False,
        )
        response = self.client.get(reverse('public:events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/events.html')
        self.assertContains(response, 'Future Event')
        self.assertContains(response, 'Current Event')
        self.assertContains(response, 'Past Event')
        self.assertNotContains(response, 'Hidden Event')
        self.assertIn(
            Event.objects.get(title='Future Event'),
            response.context['upcoming_events'],
        )
        self.assertIn(
            Event.objects.get(title='Current Event'),
            response.context['upcoming_events'],
        )
        self.assertIn(
            Event.objects.get(title='Past Event'),
            response.context['past_events'],
        )

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        INQUIRY_NOTIFICATION_EMAIL='info@loftycreekchristianschool.org',
    )
    def test_contact_submission_validates_and_normalizes(self):
        response = self.client.post(reverse('public:contact'), {
            'first_name': 'Test',
            'last_name': 'Parent',
            'email': 'parent@example.com',
            'phone_number': '0712 345 678',
            'subject': 'General Inquiry',
            'message': 'Please contact me.',
            'website': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.get().phone_number, '+254712345678')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            ['info@loftycreekchristianschool.org'],
        )
        self.assertEqual(mail.outbox[0].reply_to, ['parent@example.com'])

    def test_contact_honeypot_rejects_bots(self):
        response = self.client.post(reverse('public:contact'), {
            'first_name': 'Bot', 'last_name': 'Bot',
            'email': 'bot@example.com', 'subject': 'General Inquiry',
            'message': 'Spam', 'website': 'https://spam.example',
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ContactMessage.objects.exists())

    def test_blog_html_is_sanitized(self):
        post = BlogPost.objects.create(
            title='Safe post', excerpt='Excerpt',
            content='<p>Allowed</p><script>alert(1)</script>',
        )
        self.assertNotIn('<script', post.content)
