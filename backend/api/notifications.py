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


def notify_same_college_users(roles, message, college):
    """
       Notify users with specified roles in the same college.

       :param roles: List of roles to filter users by.
       :param message: Message to send in the notification.
       :param college: College to filter users by.
    """
    from .models import Notification, User
    try:
        users = User.objects.filter(role__in=roles, college=college)
        if not users.exists():
            looger.warning(f"No users found with roles:{roles} in college: {college}")
        for user in users:
            Notification.objects.create(user=user, message=message)
            looger.info(f"Notification was created for {user.registration_number}")
    except Exception as e:
        looger.error(f"error in notifying users: {e}")
        print(e)


def notify_user(registration_number, message):
    """
       Notify users with message

       :param message: Message to send in the notification.
    """
    from .models import Notification, User
    try:
        user = User.objects.get(registration_number=registration_number)
        Notification.objects.create(user=user, message=message)
        looger.info(f"Notification was created for {user.registration_number}")
    except user.DoesNotExist:
        looger.warning(f"No users found with {user.registration_number}")
    except Exception as e:
        looger.error(f"error in notifying user: {e}")
        print(e)


def notify_hod(role, message, branch):
    """
       Notify HOD with message

       :param message: Message to send in the notification.
    """
    from .models import Notification, User
    try:
        users = User.objects.filter(role=role, branch=branch)
        if not users.exists():
            looger.warning(f"No users found with role '{role}' and branch '{branch}'")
            return
        for user in users:
            Notification.objects.create(user=user, message=message)
            looger.info(f"Notification was created for {user.registration_number}")
    except Exception as e:
        looger.error(f"error in notifying user: {e}")
        print(e)
