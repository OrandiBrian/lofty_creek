from django.conf import settings


def site_links(request):
    return {
        'facebook_url': settings.FACEBOOK_URL,
        'instagram_url': settings.INSTAGRAM_URL,
        'youtube_url': settings.YOUTUBE_URL,
        'privacy_policy_url': settings.PRIVACY_POLICY_URL,
        'terms_of_service_url': settings.TERMS_OF_SERVICE_URL,
    }
