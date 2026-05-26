from __future__ import print_function

import logging
import africastalking
from django.conf import settings
from .models import SMSMessage

logger = logging.getLogger('sms')


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
            logger.warning(f"Aborting Campaign '{campaign.name}' (ID: {campaign.id}): No valid recipients found.")
            return {"error": "No valid recipients found."}

        # Set the numbers to send to in international format
        recipients = [contact.phone_number for contact in recipients_set if contact.phone_number]

        if not recipients:
            campaign.status = 'FAILED'
            campaign.save()
            logger.warning(f"Aborting Campaign '{campaign.name}' (ID: {campaign.id}): No valid phone numbers found among resolved recipients.")
            return {"error": "No valid phone numbers found among recipients."}

        # Set your message
        message = campaign.message_body
        logger.info(f"Resolved {len(recipients)} unique recipient phone numbers for Campaign '{campaign.name}' (ID: {campaign.id}). Message preview: '{message[:50]}...'")

        try:
            # Hit send and Africa's Talking takes care of the rest
            logger.info(f"Sending Campaign '{campaign.name}' (ID: {campaign.id}) to {len(recipients)} recipients via Africa's Talking API...")
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

            logger.info(f"Successfully processed Campaign '{campaign.name}' (ID: {campaign.id}). Dispatch status: {campaign.status}. Success count: {success_count}/{len(recipients)}, Total Cost: {total_cost}")
            return {"success": f"Sent {success_count} messages successfully out of {len(recipients)}."}

        except Exception as e:
            campaign.status = 'FAILED'
            campaign.save()
            logger.error(f"Encountered exception while sending Campaign '{campaign.name}' (ID: {campaign.id}): {str(e)}", exc_info=True)
            return {"error": "Encountered an error while sending: %s" % str(e)}

    def get_balance(self):
        """
        Fetches the remaining credits/balance from Africa's Talking.
        """
        if not self.api_key:
            return "Unconfigured"
        try:
            account = africastalking.Application
            response = account().fetch_credits()
            if isinstance(response, dict) and 'UserData' in response and 'balance' in response['UserData']:
                return response['UserData']['balance']
            return str(response)
        except Exception as e:
            logger.error(f"Error fetching balance from Africa's Talking: {e}")
            return "Unavailable"


def send_bulk_sms(campaign):
    """
    Convenience wrapper — instantiates the SMS class and sends the campaign.
    Called from views.py.
    """
    return SMS().send(campaign)


def get_sms_balance():
    """
    Convenience wrapper to retrieve remaining SMS credits/balance.
    """
    return SMS().get_balance()
