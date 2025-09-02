from django.contrib.auth.backends import BaseBackend
from .models import User


class EmailAndRegistrationBackend(BaseBackend):
    def authenticate(self, request, email=None, registration_number=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            if user.registration_number == registration_number:  # valida matrícula
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
