"""
Signal handlers for notification app.
Automatically send email notifications when Notification objects are created.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from .email_utils import send_notification_email
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def send_email_on_notification_create(sender, instance, created, **kwargs):
    """
    Send email notification when a new Notification is created.
    Only sends if user has email_notifications enabled.

    Args:
        sender: The Notification model class
        instance: The actual Notification instance being saved
        created: Boolean indicating if this is a new instance
    """
    if created:
        # Only send email for newly created notifications
        # Check if user has email notifications enabled
        if instance.recipient.email_notifications:
            try:
                send_notification_email(instance)
            except Exception as e:
                # Log error but don't prevent notification from being saved
                logger.error(f"Failed to send email for notification {instance.id}: {e}")
