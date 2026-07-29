import logging

from django.conf import settings
from django.core.mail import EmailMessage


logger = logging.getLogger(__name__)


def _send_notification(subject, body, reply_to=None):
    try:
        EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.INQUIRY_NOTIFICATION_EMAIL],
            reply_to=reply_to or [],
        ).send(fail_silently=False)
    except Exception:
        # The inquiry has already been saved. Log delivery failures without
        # making the visitor resubmit or risking a duplicate response.
        logger.exception('Unable to send website inquiry notification email.')


def notify_contact_message(message):
    phone = message.phone_number or 'Not provided'
    _send_notification(
        subject=f'New website message: {message.subject}',
        body=(
            'A new contact message was submitted on the LCCS website.\n\n'
            f'Name: {message.first_name} {message.last_name}\n'
            f'Email: {message.email}\n'
            f'Phone: {phone}\n'
            f'Subject: {message.subject}\n\n'
            f'Message:\n{message.message}\n\n'
            'Sign in to Django admin to review and mark this message as read.'
        ),
        reply_to=[message.email],
    )


def notify_admission_inquiry(inquiry):
    _send_notification(
        subject=f'New admissions inquiry: {inquiry.parent_name}',
        body=(
            'A new admissions inquiry was submitted on the LCCS website.\n\n'
            f'Parent/guardian: {inquiry.parent_name}\n'
            f'Phone: {inquiry.phone_number}\n'
            f'Grade of interest: {inquiry.get_grade_level_display()}\n\n'
            'Sign in to Django admin to review and mark this inquiry as read.'
        ),
    )
