from django import template
from djangolms.notifications.models import Notification

register = template.Library()


@register.simple_tag
def unread_notification_count(user):
    """Return the count of unread notifications for a user."""
    if not user.is_authenticated:
        return 0
    return Notification.objects.filter(recipient=user, is_read=False).count()
