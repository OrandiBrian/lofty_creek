from django.test import TestCase, Client
from django.urls import reverse

class PublicViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse('public:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/index.html')

    def test_about_view(self):
        response = self.client.get(reverse('public:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/about.html')

    def test_academics_view(self):
        response = self.client.get(reverse('public:academics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/academics.html')

    def test_admissions_view(self):
        response = self.client.get(reverse('public:admissions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/admissions.html')

    def test_gallery_view(self):
        response = self.client.get(reverse('public:gallery'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/gallery.html')

    def test_contact_view(self):
        response = self.client.get(reverse('public:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/contact.html')

    def test_resources_view(self):
        response = self.client.get(reverse('public:resources'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/resources.html')

    def test_events_view(self):
        response = self.client.get(reverse('public:events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'public/events.html')
