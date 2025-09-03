from django import forms
from .models import CustomUser


class LoginForm(forms.Form):
    registration_number = forms.CharField(max_length=8, widget=forms.TextInput(attrs={'placeholder': 'Digite seu número de matrícula'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha'}))

    def clean(self):
        cleaned_data = super().clean()
        registration_number = cleaned_data.get("registration_number")
        password = cleaned_data.get("password")

        if not registration_number or not password:
            raise forms.ValidationError("Por favor, preencha todos os campos.")

        return cleaned_data