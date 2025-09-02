from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import random
import string


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    registration_number = models.CharField(max_length=8, unique=True)

    ROLE_CHOICES = [
        ("aluno", "Aluno"),
        ("professor", "Professor"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="aluno")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


    def __str__(self):
        return f"{self.name} - {self.role}: {self.registration_number}"
    
    def save(self, *args, **kwargs):
        if not self.registration_number:
            self.registration_number = self._generate_unique_registration_number()

        if not self.password:
            self.set_password(self.registration_number)
        super().save(*args, **kwargs)

    def _generate_unique_registration_number(self):
        while True:
            reg_num = ''.join(random.choices(string.digits, k=8))  # só números
            if not User.objects.filter(registration_number=reg_num).exists():
                return reg_num
