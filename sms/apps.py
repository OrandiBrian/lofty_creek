from django.apps import AppConfig


class SmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sms'
    icon = 'fa-solid fa-paper-plane'
    divider_title = 'SMS Campaigns'
