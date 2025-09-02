from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "role")  # não inclui senha

    def clean_password2(self):
        # Sobrescreve para não exigir confirmação de senha
        return None


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "role", "registration_number")
