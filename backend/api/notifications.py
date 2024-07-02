def notify_roles(roles, message):
    from .models import Notification, User
    try:
        users = User.objects.filter(role__in=roles)
        for user in users:
            Notification.objects.create(user=user, message=message)
    except Exception as e:
        print(e)
