from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    icon = 'fa-solid fa-address-card'
    divider_title = 'Contacts & Templates'
