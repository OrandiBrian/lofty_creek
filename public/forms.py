from django import forms

from core.validators import normalize_phone_number
from .models import AdmissionInquiry, ContactMessage


class ContactMessageForm(forms.ModelForm):
    website = forms.CharField(required=False)

    class Meta:
        model = ContactMessage
        fields = (
            'first_name', 'last_name', 'email', 'phone_number', 'subject',
            'message',
        )

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Invalid submission.')
        return ''

    def clean_phone_number(self):
        value = self.cleaned_data.get('phone_number')
        return normalize_phone_number(value) if value else value


class AdmissionInquiryForm(forms.ModelForm):
    website = forms.CharField(required=False)

    class Meta:
        model = AdmissionInquiry
        fields = ('parent_name', 'phone_number', 'grade_level')

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Invalid submission.')
        return ''

    def clean_phone_number(self):
        return normalize_phone_number(self.cleaned_data.get('phone_number'))
