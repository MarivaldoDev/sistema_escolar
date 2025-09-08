from django.contrib.auth.models import AbstractUser
from django.db import models

from .utiuls.functions import (generate_unique_registration_number,
                               send_welcome_email)

# senha_geral: Abc123@00


class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    registration_number = models.CharField(max_length=8, unique=True, blank=True)

    ROLE_CHOICES = [
        ("aluno", "Aluno"),
        ("professor", "Professor"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    USERNAME_FIELD = "registration_number"
    REQUIRED_FIELDS = ["username", "email"]

    def __str__(self):
        return f"{self.username} ({self.role}) - Matrícula: {self.registration_number}"

    def save(self, *args, **kwargs):
        if not self.registration_number:
            self.registration_number = generate_unique_registration_number()
            while True:
                if not CustomUser.objects.filter(
                    registration_number=self.registration_number
                ).exists():
                    break
                self.registration_number = generate_unique_registration_number()
        try:
            send_welcome_email(self.username, self.email, self.registration_number)
        except Exception as e:
            pass
        super().save(*args, **kwargs)


class Team(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(
        "CustomUser", related_name="teams", limit_choices_to={"role": "aluno"}
    )
    year = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.year}"


class Subject(models.Model):
    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        related_name="subjects",
        limit_choices_to={"role": "professor"},
    )
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="subjects")

    def __str__(self):
        return f"{self.name} - ({self.team.name})"


class Grade(models.Model):
    student = models.ForeignKey(
        "CustomUser", on_delete=models.CASCADE, limit_choices_to={"role": "aluno"}
    )
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE)
    value = models.FloatField()
    bimonthly = models.ForeignKey("Bimonthly", on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.subject.name}: {self.value}"


class Bimonthly(models.Model):
    number = models.IntegerField(
        choices=[
            (1, "1º Bimestre"),
            (2, "2º Bimestre"),
            (3, "3º Bimestre"),
            (4, "4º Bimestre"),
        ]
    )
    year = models.IntegerField()

    def __str__(self):
        return f"{self.number}º Bimestre/{self.year}"
