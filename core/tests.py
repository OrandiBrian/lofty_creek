from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Contact, ContactGroup

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

    def test_contact_creation(self):
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(self.contact.name, 'Test Parent')
        self.assertEqual(str(self.contact), 'Test Parent (Parent)')

    def test_contact_group_creation(self):
        self.assertEqual(ContactGroup.objects.count(), 1)
        self.assertIn(self.contact, self.group.contacts.all())
        self.assertEqual(str(self.group), 'Test Group')

    def test_phone_number_is_normalized(self):
        contact = Contact.objects.create(phone_number='0712 345 678', name='Local')
        self.assertEqual(contact.phone_number, '+254712345678')

    def test_invalid_phone_number_is_rejected(self):
        with self.assertRaises(ValidationError):
            Contact.objects.create(phone_number='123', name='Invalid')
