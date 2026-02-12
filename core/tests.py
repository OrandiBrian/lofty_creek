from django.test import TestCase
from .models import Contact, ContactGroup, SMSTemplate

class CoreModelsTest(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            phone_number='+254700000000',
            name='Test Parent',
            email='test@parent.com',
            category='PARENT',
            relationship_type='Father'
        )

        self.group = ContactGroup.objects.create(
            name='Test Group',
            description='Group for testing'
        )
        self.group.contacts.add(self.contact)

        self.template = SMSTemplate.objects.create(
            name='Welcome Template',
            content='Welcome to LCCS {name}'
        )

    def test_contact_creation(self):
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(self.contact.name, 'Test Parent')
        self.assertEqual(str(self.contact), 'Test Parent (Parent)')

    def test_contact_group_creation(self):
        self.assertEqual(ContactGroup.objects.count(), 1)
        self.assertIn(self.contact, self.group.contacts.all())
        self.assertEqual(str(self.group), 'Test Group')

    def test_sms_template_creation(self):
        self.assertEqual(SMSTemplate.objects.count(), 1)
        self.assertEqual(self.template.name, 'Welcome Template')
        self.assertEqual(str(self.template), 'Welcome Template')
