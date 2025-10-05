import random
import string

from django.core.mail import send_mail


def generate_unique_registration_number() -> str:
    while True:
        reg_num = "".join(random.choices(string.digits, k=8))
        return reg_num


def send_welcome_email(user: str, email: str, registration_number: str) -> None:
    subject = "Bem-vindo ao Sistema Escolar"
    message = f"Olá {user},\n\nBem-vindo ao nosso sistema escolar!\nSua matrícula é {registration_number}. Guarde-a com cuidado!"
    send_mail(subject, message, "from@example.com", [email])


def is_aproved(grades: list, bimonthlys: list) -> bool:
    if len(grades) != len(bimonthlys):
        return False
    media = sum(grades) / len(grades)

    if media >= 6:
        return True
    return False