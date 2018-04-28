from django.apps import AppConfig


class DRFMessagingConfig(AppConfig):
    name = 'drf_messaging'
    verbose_name = "Messages"

    def ready(self):
        from . import signals
