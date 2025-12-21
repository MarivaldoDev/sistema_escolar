from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .utiuls.functions import (generate_unique_registration_number,
                               send_welcome_email)

# senha_geral: Abc123@00


class CustomUserManager(BaseUserManager):
    def create_user(
        self, registration_number, email=None, password=None, **extra_fields
    ):
        if not registration_number:
            raise ValueError("O campo registration_number é obrigatório")
        if not email:
            raise ValueError("O campo email é obrigatório para usuários comuns")

        email = self.normalize_email(email)
        user = self.model(
            registration_number=registration_number, email=email, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, registration_number, email=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        # permitir email None para criação via linha de comando, mas garantir valor não-NULL ao salvar
        email_value = self.normalize_email(email) if email else ""
        user = self.model(
            registration_number=registration_number, email=email_value, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    registration_number = models.CharField(max_length=8, unique=True, blank=True)
    image_profile = models.ImageField(blank=True, upload_to="imagem_cadastro/%Y/%m/")

    ROLE_CHOICES = [
        ("aluno", "Aluno"),
        ("professor", "Professor"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    USERNAME_FIELD = "registration_number"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role}) - Matrícula: {self.registration_number}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        # Garantir primeiro um registration_number único, depois gerar username a partir dele.
        if not self.registration_number:
            self.registration_number = generate_unique_registration_number()
            while CustomUser.objects.filter(
                registration_number=self.registration_number
            ).exists():
                self.registration_number = generate_unique_registration_number()
        if not self.username:
            self.username = f"user_{self.registration_number}"
        if is_new:
            try:
                send_welcome_email(
                    self.first_name, self.email, self.registration_number
                )
            except Exception:
                pass
        super().save(*args, **kwargs)


class Team(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(
        "CustomUser", related_name="teams", limit_choices_to={"role": "aluno"}
    )
    year = models.IntegerField()

    def clean(self):
        if not self.pk:
            return
        for member in self.members.all():
            if member.role != "aluno":
                raise ValidationError(
                    f"{member} não pode ser adicionado — não é aluno."
                )

    def __str__(self):
        return f"{self.name} - {self.year}"


class Subject(models.Model):
    name = models.CharField(max_length=50)
    teachers = models.ManyToManyField(
        "CustomUser",
        related_name="subjects",
        limit_choices_to={"role": "professor"},
        blank=True,
    )
    team = models.ManyToManyField(Team, related_name="subjects")

    def __str__(self):
        return self.name

    def clean(self):
        if not self.pk:
            return
        for teacher in self.teachers.all():
            if teacher.role != "professor":
                raise ValidationError(
                    "Apenas usuários com papel de professor podem ser adicionados como professores."
                )


class Grade(models.Model):
    student = models.ForeignKey(
        "CustomUser", on_delete=models.CASCADE, limit_choices_to={"role": "aluno"}
    )
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE, null=True, blank=True)
    value_activity = models.FloatField()
    value_proof = models.FloatField()
    average = models.FloatField(null=True, blank=True)
    bimonthly = models.ForeignKey("Bimonthly", on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} ({self.bimonthly}) - {self.subject.name}: {self.average}"

    def clean(self):
        if self.value_activity < 0 or self.value_proof < 0.0:
            raise ValidationError("Nenhuma nota pode ser menor que 0.0.")
        if self.value_activity > 10.0 or self.value_proof > 10.0:
            raise ValidationError("Nenhuma nota pode ser maior que 10.0.")

    def save(self, *args, **kwargs):
        self.average = (self.value_activity + self.value_proof) / 2
        super().save(*args, **kwargs)


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


class Attendance(models.Model):
    teacher = models.ForeignKey(
        "CustomUser", on_delete=models.CASCADE, limit_choices_to={"role": "professor"}
    )
    team = models.ForeignKey("Team", on_delete=models.CASCADE)
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Chamada - {self.team.name} / {self.subject.name} ({self.date})"


class AttendanceRecord(models.Model):
    attendance = models.ForeignKey(
        "Attendance", on_delete=models.CASCADE, related_name="records"
    )
    student = models.ForeignKey(
        "CustomUser", on_delete=models.CASCADE, limit_choices_to={"role": "aluno"}
    )
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.first_name} - {'Presente' if self.present else 'Faltou'}"
    
