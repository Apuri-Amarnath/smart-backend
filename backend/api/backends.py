from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationNumberBackend(BaseBackend):
    def authenticate(self, request, registration_number=None, password=None, **kwargs):
        try:
            user = User.objects.get(registration_number=registration_number)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
