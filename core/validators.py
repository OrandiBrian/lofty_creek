import re

from django.core.exceptions import ValidationError


def normalize_phone_number(value):
    """Return a Kenyan phone number in E.164 format."""
    raw = re.sub(r'[\s().-]', '', str(value or '').strip())
    if raw.startswith('00'):
        raw = f'+{raw[2:]}'
    elif raw.startswith('0'):
        raw = f'+254{raw[1:]}'
    elif raw.startswith('254'):
        raw = f'+{raw}'

    if not re.fullmatch(r'\+254[17]\d{8}', raw):
        raise ValidationError('Enter a valid Kenyan mobile number, e.g. +254712345678.')
    return raw


def validate_image_size(image):
    if image and image.size > 5 * 1024 * 1024:
        raise ValidationError('Images must be 5 MB or smaller.')


def validate_document_size(document):
    if document and document.size > 10 * 1024 * 1024:
        raise ValidationError('Documents must be 10 MB or smaller.')
