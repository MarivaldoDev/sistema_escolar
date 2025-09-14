from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, GradeForm
from .models import Team, CustomUser, Subject


def home(request):
    return render(request, "home.html")


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
            return redirect("home")
    return render(request, "login.html", {"form": form})


def my_logout(request):
    logout(request)
    return redirect("login")


def turmas(request):
    user = request.user
    if user.role == 'professor' and not user.is_superuser:
        turmas = Team.objects.filter(subjects__teacher=user).distinct()
    else:   
        turmas = Team.objects.all()
    return render(request, "turmas.html", {"turmas": turmas})


def turma_detail(request, team_id: int):
    user = request.user
    subject = Subject.objects.filter(teacher=user).first()
    if user.role == "professor" and not user.is_superuser:
        turma = get_object_or_404(Team, id=team_id, subjects__teacher=user)
    else:
        turma = get_object_or_404(Team, id=team_id)

    return render(request, "turma_detail.html", {"turma": turma, "subject": subject.name})


def add_grade(request, team_id: int, subject_name: str, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, name=subject_name)

    if student not in team.members.all():
        return redirect("turma_detail", team_id=team_id)

    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.subject = subject
            grade.team = team
            grade.save()
            return redirect("turma_detail", team_id=team_id)
    else:
        form = GradeForm()

    return render(
        request,
        "add_grade.html",
        {"form": form, "student": student, "subject": subject, "team": team},
    )

