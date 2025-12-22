import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from notifications.models import Notification

from ..forms import LoginForm
from ..models import CustomUser, Grade, Team
from ..notifications import get_unread_notifications
from ..utiuls.functions import is_aproved

logger = logging.getLogger(__name__)


def home(request):
    unread_notifications_count = (
        get_unread_notifications(request.user).count()
        if request.user.is_authenticated
        else 0
    )
    return render(
        request, "home.html", {"unread_notifications_count": unread_notifications_count}
    )


def my_login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    form = LoginForm(request.POST)
    if form.is_valid():
        registration_number = form.cleaned_data["registration_number"]
        password = form.cleaned_data["password"]
        user = authenticate(
            request, registration_number=registration_number, password=password
        )

        if user is not None:
            login(request, user)
            logger.info("Usuário fez login com sucesso")
            return redirect("home")
        else:
            logger.warning("Falha no login: número de matrícula ou senha inválidos")
            messages.error(request, "Número de matrícula ou senha inválidos.")
    else:
        for error in form.errors:
            messages.error(request, form.errors[error])

    return render(request, "login.html", {"form": form})


def my_logout(request):
    logout(request)
    logger.info("Usuário fez logout com sucesso")
    return redirect("login")


def search(request):
    student = get_object_or_404(CustomUser, id=request.user.id)
    team = Team.objects.filter(members=student).first()
    subjects = team.subjects.all() if team else []
    grades = Grade.objects.filter(student=student)

    search_value = request.GET.get("q", "").strip()

    if search_value:
        subjects = subjects.filter(Q(name__icontains=search_value))

    subjects_with_grades = []
    max_bimonthlys = 0
    for subject in subjects:
        subject_grades = grades.filter(subject=subject, team=team).order_by(
            "bimonthly__number"
        )
        grade_values = [g.value for g in subject_grades]
        bimonthlys = [str(g.bimonthly) for g in subject_grades]
        if len(bimonthlys) > max_bimonthlys:
            max_bimonthlys = len(bimonthlys)

        if grade_values:
            aprovado = is_aproved(grade_values, bimonthlys)
            media = sum(grade_values) / len(grade_values)
        else:
            aprovado = False
            media = None

        subjects_with_grades.append(
            {
                "subject": subject,
                "grades": subject_grades,
                "status": "Aprovado" if aprovado else "Reprovado",
                "media": media,
            }
        )

    return render(
        request,
        "my_grades.html",
        {
            "student": student,
            "team": team,
            "subjects_with_grades": sorted(
                subjects_with_grades, key=lambda x: x["subject"].name
            ),
            "search_value": search_value,
            "bimonthlys": max_bimonthlys,
        },
    )


def acesso_negado(request, mensagem: str):
    return HttpResponseForbidden(
        render(request, "acesso_negado.html", {"mensagem": mensagem})
    )


def list_notifications(request):
    unread_notifications = get_unread_notifications(request.user)
    return render(
        request, "notifications.html", {"notifications": unread_notifications}
    )


def mark_notifications_as_read(request):
    Notification.objects.mark_all_as_read(recipient=request.user)
    return redirect(reverse("list_notifications"))
