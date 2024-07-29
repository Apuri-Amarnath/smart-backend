import logging

from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_login_credentials(registration_number, password, to_email):
    url = f'http://127.0.0.1:8000/api/user/login/'
    subject = 'Your Login Credentials for Smartone'
    message = f'Your account has been created with the following credentials:\n\n' \
              f'Registration Number: {registration_number}\n' \
              f'Password: {password}\n' \
              f'Login URL: {url}\n' \
              f'Please change your password after logging in.'

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = to_email
    try:
        send_mail(subject, message, from_email, [to_email])
        logger.info(f'Login credentials email sent to {to_email}')
    except Exception as e:
        logger.error(f'Failed to send email to {to_email}: {e}')

