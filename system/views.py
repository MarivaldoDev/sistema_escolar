from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse

from .forms import GradeForm, LoginForm, GradeUpdateForm
from .models import CustomUser, Subject, Team


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
    if user.role == "professor" and not user.is_superuser:
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

    return render(
        request, "turma_detail.html", {"turma": turma, "subject": subject.name}
    )


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


def update_grade(request, team_id: int, subject_name: str, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, name=subject_name)

    if student not in team.members.all():
        return redirect("turma_detail", team_id=team_id)
    
    grade_instance = student.grade_set.filter(subject=subject).first()

    if request.method == "POST":
        form = GradeUpdateForm(request.POST, instance=grade_instance)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.subject = subject
            grade.save()
            return redirect("turma_detail", team_id=team_id)
    else:
        form = GradeUpdateForm(instance=grade_instance)

    return render(request, "update_grade.html", {"form": form, "student": student, "subject": subject, "team": team})


from django.shortcuts import render, get_object_or_404, redirect
from .models import CustomUser, Team, Subject, Grade


def my_grades(request, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)

    # garante que o aluno só veja as próprias notas
    if request.user != student:
        return redirect("home")

    # turma do aluno
    team = Team.objects.filter(members=student).first()

    if not team:
        return render(request, "grades/my_grades.html", {
            "student": student,
            "team": None,
            "subjects_with_grades": [],
        })

    # disciplinas da turma
    subjects = team.subjects.all()

    # notas do aluno
    grades = Grade.objects.filter(student=student)

    # organiza as notas por disciplina
    subjects_with_grades = []
    for subject in subjects:
        subject_grades = grades.filter(subject=subject)
        subjects_with_grades.append({
            "subject": subject,
            "grades": subject_grades
        })

    context = {
        "student": student,
        "team": team,
        "subjects_with_grades": subjects_with_grades,
    }

    return render(request, "my_grades.html", context)
