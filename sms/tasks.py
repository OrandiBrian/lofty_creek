from celery import shared_task
from django.utils import timezone

from .models import SMSCampaign
from .services import send_bulk_sms


@shared_task(bind=True, max_retries=3)
def send_campaign_task(self, campaign_id):
    campaign = SMSCampaign.objects.get(pk=campaign_id)
    result = send_bulk_sms(campaign)
    if 'error' in result and self.request.retries < self.max_retries:
        campaign.status = 'QUEUED'
        campaign.save(update_fields=['status', 'updated_at'])
        raise self.retry(countdown=30 * (2 ** self.request.retries))
    return result


def dispatch_campaign(campaign):
    """Queue production sends and keep local development deterministic."""
    from django.conf import settings

    if settings.SMS_SEND_ASYNC:
        send_campaign_task.delay(campaign.pk)
        return {'success': 'Campaign queued for background delivery.'}
    return send_bulk_sms(campaign)


@shared_task
def send_due_campaigns():
    campaign_ids = list(
        SMSCampaign.objects.filter(
            status='QUEUED',
            scheduled_at__isnull=False,
            scheduled_at__lte=timezone.now(),
        ).values_list('pk', flat=True)
    )
    for campaign_id in campaign_ids:
        send_campaign_task.delay(campaign_id)
    return len(campaign_ids)
