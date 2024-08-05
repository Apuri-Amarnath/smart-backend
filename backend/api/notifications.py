import logging

looger = logging.getLogger(__name__)


def notify_roles(roles: object, message: object) -> object:
    from .models import Notification, User
    try:
        users = User.objects.filter(role__in=roles)
        if not users.exists():
            looger.warning(f"No users found with roles:{roles}")
        for user in users:
            Notification.objects.create(user=user, message=message)
            looger.info(f"Notification was created for user: {user.registration_number}")
    except Exception as e:
        looger.error(f"error in notifying users: {e}")
        print(e)
