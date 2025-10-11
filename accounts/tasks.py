from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_async_email(subject, message, from_email, recipient_list, html_message=None):
    """
    Celery task to send an email asynchronously.
    
    Args:
        subject (str): Email subject
        message (str): Plain text email body
        from_email (str): Sender email address
        recipient_list (list): List of recipient email addresses
        html_message (str, optional): HTML email body
    """
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        
        if html_message:
            email.attach_alternative(html_message, "text/html")
        
        email.send()
        logger.info("Successfully sent email to %s with subject: %s", recipient_list, subject)
    except Exception as e:
        logger.error("Failed to send email to %s: %s", recipient_list, str(e))
        raise