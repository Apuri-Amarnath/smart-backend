import logging

from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_login_credentials(registration_number, password, to_email, college_name):
    url = f'http://127.0.0.1:8000/api/user/login/'
    subject = 'Your Login Credentials for Smartone'
    message = f"""
        Dear {college_name},

        Your account has been created with the following credentials:

        Registration Number: {registration_number}
        Password: {password}
        Login URL: {url}

        Please log in using the above credentials and change your password immediately.

        If you have any questions, please contact support.

        Best regards,
        The Smartone Team
        """
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = to_email
    try:
        send_mail(subject, message, from_email, [to_email])
        logger.info(f'Login credentials email sent to {to_email}')
    except Exception as e:
        logger.error(f'Failed to send email to {to_email}: {e}')


def send_HOD_login_credentials(registration_number, password, to_email, college_name, branch):
    url = f'http://127.0.0.1:8000/api/user/login/'
    subject = f'Your {branch} HOD Login Credentials for Smartone'
    message = f"""
        Dear {college_name},

        Your account has been created with the following credentials:

        Registration Number: {registration_number}
        Password: {password}
        Login URL: {url}

        Please log in using the above credentials and change your password immediately.

        If you have any questions, please contact support.

        Best regards,
        The Smartone Team
        """
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = to_email
    try:
        send_mail(subject, message, from_email, [to_email])
        logger.info(f'Login credentials email sent to {to_email}')
    except Exception as e:
        logger.error(f'Failed to send email to {to_email}: {e}')


def send_department_login_credentials(credentials, to_email, college_name):
    url = f'http://127.0.0.1:8000/api/user/login/'
    subject = f'Your department Login Credentials for Smartone'
    message = f"""
        Dear {college_name},

        Your account has been created with the following credentials:

        """
    for registration_number, password, department_number in credentials:
        message += f"""
        Department Number: {department_number}
        Registration Number: {registration_number}
        Password: {password}
        """

        message += f"""
        Login URL: {url}

        Please log in using the above credentials and change your password immediately.

        If you have any questions, please contact support.

        Best regards,
        The Smartone Team
        """
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = to_email
    try:
        send_mail(subject, message, from_email, [to_email])
        logger.info(f'Login credentials email sent to {to_email}')
    except Exception as e:
        logger.error(f'Failed to send email to {to_email}: {e}')
