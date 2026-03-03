from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Contact
from sms.models import SMSCampaign, SMSMessage

class SMSAppTest(TestCase):
    def setUp(self):
        # Create a staff user for view tests
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='testpassword123',
            is_staff=True
        )

        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regularuser',
            password='testpassword123',
            is_staff=False
        )

        # Content for models
        self.contact = Contact.objects.create(
            phone_number='+254711000000',
            name='Test Contact',
            category='PARENT'
        )

        self.campaign = SMSCampaign.objects.create(
            name='Test Campaign',
            message_body='Hello from the test side.',
            status='DRAFT'
        )
        self.campaign.recipients.add(self.contact)

        self.message = SMSMessage.objects.create(
            campaign=self.campaign,
            contact=self.contact,
            message_body='Hello from the test side.',
            status='PENDING',
            cost=0.0
        )
        
        self.client = Client()

    def test_campaign_creation(self):
        self.assertEqual(SMSCampaign.objects.count(), 1)
        self.assertEqual(self.campaign.name, 'Test Campaign')
        self.assertEqual(str(self.campaign), 'Test Campaign - DRAFT')

    def test_message_creation(self):
        self.assertEqual(SMSMessage.objects.count(), 1)
        self.assertEqual(self.message.contact.name, 'Test Contact')
        self.assertEqual(str(self.message), 'To +254711000000 - PENDING')

    def test_overview_view_redirects_non_staff(self):
        self.client.login(username='regularuser', password='testpassword123')
        response = self.client.get(reverse('sms:overview'))
        # Should redirect to admin login because of @staff_member_required
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/admin/login/' in response.url)

    def test_overview_view_staff_access(self):
        self.client.login(username='staffuser', password='testpassword123')
        response = self.client.get(reverse('sms:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sms/overview.html')

    def test_compose_view_staff_access(self):
        self.client.login(username='staffuser', password='testpassword123')
        response = self.client.get(reverse('sms:compose'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sms/compose.html')

    def test_contacts_view_staff_access(self):
        self.client.login(username='staffuser', password='testpassword123')
        response = self.client.get(reverse('sms:contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sms/contacts.html')
