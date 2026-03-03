from __future__ import print_function

import africastalking
from django.conf import settings
from .models import SMSMessage


class SMS:
    def __init__(self):
        # Set your app credentials from Django settings / .env
        self.username = getattr(settings, 'AFRICASTALKING_USERNAME', 'sandbox')
        self.api_key = getattr(settings, 'AFRICASTALKING_API_KEY', '')
        self.sender_id = getattr(settings, 'AFRICASTALKING_SENDER_ID', None)

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS

    def send(self, campaign):
        """
        Sends bulk SMS for a given SMSCampaign.
        Collects recipients from individual contacts and groups,
        deduplicates them, then sends via Africa's Talking.
        """
        if not self.api_key:
            campaign.status = 'FAILED'
            campaign.save()
            return {"error": "Africa's Talking API key is not configured. Set AFRICASTALKING_API_KEY in your .env file."}

        if campaign.status != 'QUEUED':
            return {"error": "Campaign is not queued for sending."}

        campaign.status = 'SENDING'
        campaign.save()

        # Collect unique recipients (set handles deduplication)
        recipients_set = set()

        # Add individual recipients
        for contact in campaign.recipients.all():
            recipients_set.add(contact)

        # Add group recipients
        for group in campaign.recipient_groups.all():
            for contact in group.contacts.all():
                recipients_set.add(contact)

        if not recipients_set:
            campaign.status = 'FAILED'
            campaign.save()
            return {"error": "No valid recipients found."}

        # Set the numbers to send to in international format
        recipients = [contact.phone_number for contact in recipients_set if contact.phone_number]

        if not recipients:
            campaign.status = 'FAILED'
            campaign.save()
            return {"error": "No valid phone numbers found among recipients."}

        # Set your message
        message = campaign.message_body

        try:
            # Hit send and Africa's Talking takes care of the rest
            if self.sender_id:
                response = self.sms.send(message, recipients, self.sender_id)
            else:
                response = self.sms.send(message, recipients)

            success_count = 0
            total_cost = 0.0

            # Parse per-recipient delivery data from AT response
            if 'SMSMessageData' in response and 'Recipients' in response['SMSMessageData']:
                for recipient_data in response['SMSMessageData']['Recipients']:
                    number = recipient_data.get('number')
                    status = recipient_data.get('status')
                    message_id = recipient_data.get('messageId')
                    cost_str = recipient_data.get('cost', '0')
                    cost_val = float(cost_str.split(' ')[-1]) if ' ' in cost_str else 0.0

                    # Match the phone number back to our Contact object
                    contact = next(
                        (c for c in recipients_set
                         if c.phone_number == number or c.phone_number == number.replace('+', '')),
                        None
                    )

                    if contact:
                        SMSMessage.objects.create(
                            campaign=campaign,
                            contact=contact,
                            message_body=campaign.message_body,
                            at_message_id=message_id,
                            status='SENT' if status == 'Success' else 'FAILED',
                            cost=cost_val
                        )

                        if status == 'Success':
                            success_count += 1
                            total_cost += cost_val

            # Update campaign status and cost
            campaign.total_cost = total_cost
            campaign.status = 'SENT' if success_count > 0 else 'FAILED'
            campaign.save()

            return {"success": f"Sent {success_count} messages successfully out of {len(recipients)}."}

        except Exception as e:
            campaign.status = 'FAILED'
            campaign.save()
            return {"error": "Encountered an error while sending: %s" % str(e)}


def send_bulk_sms(campaign):
    """
    Convenience wrapper — instantiates the SMS class and sends the campaign.
    Called from views.py.
    """
    return SMS().send(campaign)
