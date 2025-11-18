from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangolms.notifications'

    def ready(self):
        """Import signal handlers when app is ready."""
        import djangolms.notifications.signals  # noqa
