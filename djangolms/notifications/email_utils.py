"""
Email notification utilities for sending email notifications to users.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_notification_email(notification):
    """
    Send an email notification to the recipient.

    Args:
        notification: Notification model instance

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not notification.recipient.email:
        logger.warning(f"User {notification.recipient.username} has no email address")
        return False

    try:
        # Prepare context for email template
        context = {
            'notification': notification,
            'recipient': notification.recipient,
            'site_name': getattr(settings, 'SITE_NAME', 'USIU LMS'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }

        # Render HTML and plain text versions
        html_content = render_to_string(
            'notifications/email/notification_email.html',
            context
        )
        text_content = strip_tags(html_content)

        # Create email
        subject = f"[{context['site_name']}] {notification.title}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = notification.recipient.email

        # Create message with both HTML and plain text
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        email.attach_alternative(html_content, "text/html")

        # Send email
        email.send(fail_silently=False)
        logger.info(f"Sent email notification to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False


def send_bulk_notification_emails(notifications):
    """
    Send multiple email notifications efficiently.

    Args:
        notifications: QuerySet or list of Notification instances

    Returns:
        tuple: (success_count, failure_count)
    """
    success_count = 0
    failure_count = 0

    for notification in notifications:
        if send_notification_email(notification):
            success_count += 1
        else:
            failure_count += 1

    return success_count, failure_count


def send_custom_email(recipient, subject, message, html_message=None):
    """
    Send a custom email to a user.

    Args:
        recipient: User instance
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML message

    Returns:
        bool: True if email was sent successfully
    """
    if not recipient.email:
        logger.warning(f"User {recipient.username} has no email address")
        return False

    try:
        from_email = settings.DEFAULT_FROM_EMAIL

        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[recipient.email]
        )

        if html_message:
            email.attach_alternative(html_message, "text/html")

        email.send(fail_silently=False)
        logger.info(f"Sent custom email to {recipient.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send custom email: {e}")
        return False
