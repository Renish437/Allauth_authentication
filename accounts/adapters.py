from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from allauth.account.utils import user_display, user_pk_to_url_str
from allauth.utils import build_absolute_uri
from allauth.account.models import EmailAddress
from accounts.tasks import send_async_email
import logging

logger = logging.getLogger(__name__)

class CustomAccountAdapter(DefaultAccountAdapter):
    
  def get_current_date(self):
        """Return formatted current date"""
        from datetime import datetime
        return datetime.now().strftime('%Y/%m/%d')
  def send_mail(self, template_prefix, email, context):
    """Send email asynchronously with HTML content"""
    try:
        user = context.get('user', None)

        # Handle password reset separately
        if template_prefix == 'account/email/password_reset':
            if user:
                temp_key = self.generate_password_reset_key(user)
                if temp_key:
                    reset_url = self.get_password_reset_url(context.get('request'), temp_key)
                    context['reset_url'] = reset_url
                    context['timeout'] = getattr(settings, "PASSWORD_RESET_TIMEOUT", 3600)
                else:
                    logger.warning(
                        "No verified email for user %s, cannot generate reset_url",
                        user_display(user) or 'unknown'
                    )
                    context['reset_url'] = None
                    context['timeout'] = getattr(settings, "PASSWORD_RESET_TIMEOUT", 3600)
            else:
                logger.warning("No user provided for password reset email to %s", email)
                context['reset_url'] = None
                context['timeout'] = getattr(settings, "PASSWORD_RESET_TIMEOUT", 3600)

        # Defaults
        context.setdefault('user_display', user_display(user) if user else 'User')
        context.setdefault('site_name', getattr(settings, 'SITE_NAME', 'MYAUTHALL'))
        site_domain = get_current_site(context.get('request')).domain
        context.setdefault(
            'site_url',
            f"{getattr(settings, 'ACCOUNT_DEFAULT_HTTP_PROTOCOL', 'http')}://{site_domain}"
        )
        context.setdefault('current_date', self.get_current_date())

        # Render and queue email
        msg = self.render_mail(template_prefix, email, context)

        logger.debug(
            "Queueing email to %s with subject: %s, context: %s",
            email, msg.subject, context
        )

        send_async_email.delay(
            subject=msg.subject,
            message=msg.body,
            from_email=msg.from_email,
            recipient_list=msg.to,
            html_message=msg.alternatives[0][0] if msg.alternatives else None,
        )

    except Exception as e:
        logger.error("Failed to send email to %s: %s", email, str(e))
        raise


    def generate_password_reset_key(self, user):
        """Generate temporary key for password reset"""
        from allauth.account import app_settings
        self.uid = user_pk_to_url_str(user)
        email_address = EmailAddress.objects.filter(user=user, verified=True).first()
        if email_address:
            return self.generate_temporary_key(user, app_settings.PASSWORD_RESET_TOKEN_GENERATOR)
        return None

    def get_password_reset_url(self, request, temp_key):
        """Generate password reset URL"""
        current_site = get_current_site(request) or get_current_site(None)
        if not current_site.domain:
            logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
            raise ValueError("Site domain not configured")
        path = reverse("account_reset_password_from_key", kwargs={"uidb36": self.uid, "key": temp_key})
        return build_absolute_uri(request, path, protocol=settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL)

    def generate_temporary_key(self, user, token_generator):
        """Generate a temporary key using the token generator"""
        from allauth.account.utils import generate_unique_key
        email_address = EmailAddress.objects.filter(user=user, verified=True).first()
        if email_address:
            return generate_unique_key(email_address.email, token_generator)
        return None

    def send_password_reset_code(self, request, user, code):
        """Send password reset code email (for login-by-code)"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            reset_url = f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}{reverse('account_reset_password_from_code')}"
            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'reset_code': code,
                'reset_url': reset_url,
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
                'timeout': settings.ACCOUNT_LOGIN_BY_CODE_TIMEOUT,
            }

            logger.debug("Sending password reset code email to %s with context: %s", user.email, context)
            self.send_mail('account/email/password_reset_message', user.email, context)
        except Exception as e:
            logger.error("Failed to queue password reset code email for %s: %s", user.email, str(e))
            raise

    def send_password_changed_email(self, request, user):
        """Send password set/changed notification email"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
            }

            logger.debug("Sending password changed email to %s with context: %s", user.email, context)
            self.send_mail('account/email/password_changed', user.email, context)
        except Exception as e:
            logger.error("Failed to queue password changed email for %s: %s", user.email, str(e))
            raise

    def send_unknown_account_email(self, request, email):
        """Send email for password reset attempt on non-existent account"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            signup_url = reverse('account_signup')
            signup_url = f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}{signup_url}"

            context = {
                'email': email,
                'user_display': 'User',
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
                'timeout': settings.ACCOUNT_PASSWORD_RESET_TIMEOUT or 3600,
            }

            logger.debug("Sending unknown account email to %s with context: %s", email, context)
            self.send_mail('account/email/password_reset_message', email, context)
        except Exception as e:
            logger.error("Failed to queue unknown account email for %s: %s", email, str(e))
            raise

    def send_email_deleted_notification(self, request, user, deleted_email):
        """Send email deletion notification"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'deleted_email': deleted_email,
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
            }

            logger.debug("Sending email deleted notification to %s with context: %s", user.email, context)
            self.send_mail('account/email/email_deleted', user.email, context)
        except Exception as e:
            logger.error("Failed to queue email deleted notification for %s: %s", user.email, str(e))
            raise

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """Send email confirmation message"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            activate_url = self.get_email_confirmation_url(request, emailconfirmation)

            context = {
                'user': emailconfirmation.email_address.user,
                'user_display': user_display(emailconfirmation.email_address.user) or 'User',
                'email': emailconfirmation.email_address.email,
                'activate_url': activate_url,
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
                'timeout': settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS * 24 * 3600,
            }

            logger.debug("Sending email confirmation to %s with context: %s", emailconfirmation.email_address.email, context)
            self.send_mail('account/email/email_confirmation_message', emailconfirmation.email_address.email, context)
        except Exception as e:
            logger.error("Failed to queue email confirmation for %s: %s", emailconfirmation.email_address.email, str(e))
            raise

    def send_email_confirmed_notification(self, request, user, email):
        """Send email confirmed notification"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'email': email,
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
            }

            logger.debug("Sending email confirmed notification to %s with context: %s", email, context)
            self.send_mail('account/email/email_confirmed', email, context)
        except Exception as e:
            logger.error("Failed to queue email confirmed notification for %s: %s", email, str(e))
            raise

    def send_email_changed_notification(self, request, user, from_email, to_email):
        """Send email changed notification"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'from_email': from_email,
                'to_email': to_email,
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
            }

            logger.debug("Sending email changed notification to %s with context: %s", to_email, context)
            self.send_mail('account/email/email_changed', to_email, context)
        except Exception as e:
            logger.error("Failed to queue email changed notification for %s: %s", to_email, str(e))
            raise

    def send_account_change_notification(self, request, user, ip, user_agent, timestamp):
        """Send account change notification"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'ip': ip,
                'user_agent': user_agent,
                'timestamp': timestamp,
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
            }

            logger.debug("Sending account change notification to %s with context: %s", user.email, context)
            self.send_mail('account/email/account_change_notification', user.email, context)
        except Exception as e:
            logger.error("Failed to queue account change notification for %s: %s", user.email, str(e))
            raise
    
    def send_authenticator_activated_notification(self, request, user):
        """Send authenticator app activated notification"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
            }

            logger.debug("Sending authenticator activated notification to %s with context: %s", user.email, context)
            self.send_mail('account/email/authenticator_activated_message', user.email, context)
        except Exception as e:
            logger.error("Failed to queue authenticator activated notification for %s: %s", user.email, str(e))
            raise

    def send_authenticator_deactivated_notification(self, request, user):
        """Send authenticator app deactivated notification"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
            }

            logger.debug("Sending authenticator deactivated notification to %s with context: %s", user.email, context)
            self.send_mail('account/email/authenticator_deactivated_message', user.email, context)
        except Exception as e:
            logger.error("Failed to queue authenticator deactivated notification for %s: %s", user.email, str(e))
            raise

    def send_security_key_added_notification(self, request, user):
        """Send security key added notification"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
            }

            logger.debug("Sending security key added notification to %s with context: %s", user.email, context)
            self.send_mail('account/email/security_key_added_message', user.email, context)
        except Exception as e:
            logger.error("Failed to queue security key added notification for %s: %s", user.email, str(e))
            raise

    def send_security_key_removed_notification(self, request, user):
        """Send security key removed notification"""
        try:
            current_site = get_current_site(request) or get_current_site(None)
            if not current_site.domain:
                logger.error("Site domain not set for SITE_ID=%s", settings.SITE_ID)
                raise ValueError("Site domain not configured")

            context = {
                'user': user,
                'user_display': user_display(user) or 'User',
                'site_name': settings.SITE_NAME or 'MYAUTHALL',
                'site_url': f"{settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL}://{current_site.domain}",
                'current_date': self.get_current_date(),
            }

            logger.debug("Sending security key removed notification to %s with context: %s", user.email, context)
            self.send_mail('account/email/security_key_removed_message', user.email, context)
        except Exception as e:
            logger.error("Failed to queue security key removed notification for %s: %s", user.email, str(e))
            raise

