from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render

from .forms import GradeForm, GradeUpdateForm, LoginForm
from .models import CustomUser, Grade, Subject, Team


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


def search(request):
    student = get_object_or_404(CustomUser, id=request.user.id)
    team = Team.objects.filter(members=student).first()
    subjects = team.subjects.all() if team else []
    grades = Grade.objects.filter(student=student)

    search_value = request.GET.get("q", "").strip()

    if search_value:
        subjects = subjects.filter(Q(name__icontains=search_value))

    subjects_with_grades = []
    for subject in subjects:
        subject_grades = grades.filter(subject=subject)
        subjects_with_grades.append({"subject": subject, "grades": subject_grades})

    return render(
        request,
        "my_grades.html",
        {
            "student": student,
            "team": team,
            "subjects_with_grades": subjects_with_grades,
            "search_value": search_value,
        },
    )


def turmas(request):
    user = request.user
    if user.role == "professor" and not user.is_superuser:
        turmas = Team.objects.filter(subjects__teacher=user).distinct()
        subject = Subject.objects.filter(teacher=user).first()
        return render(request, "turmas.html", {"turmas": turmas, "subject": subject})
    else:
        turmas = Team.objects.all()
    return render(request, "turmas.html", {"turmas": turmas})


def turma_detail(request, team_id: int, subject_id: int):
    user = request.user

    if user.role == "professor" and not user.is_superuser:
        turma = get_object_or_404(Team, id=team_id, subjects__teacher=user)
        subject = get_object_or_404(turma.subjects, id=subject_id, teacher=user)
    else:
        turma = get_object_or_404(Team, id=team_id)
        subject = get_object_or_404(turma.subjects, id=subject_id)

    return render(
        request,
        "turma_detail.html",
        {"turma": turma, "subject": subject},
    )


def add_grade(request, team_id: int, subject_id: int, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

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


def update_grade(request, team_id: int, subject_id: int, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

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

    return render(
        request,
        "update_grade.html",
        {"form": form, "student": student, "subject": subject, "team": team},
    )


def my_grades(request, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)

    if request.user != student:
        return redirect("home")

    team = Team.objects.filter(members=student).first()

    if not team:
        return render(
            request,
            "my_grades.html",
            {
                "student": student,
                "team": None,
                "subjects_with_grades": [],
            },
        )

    subjects = team.subjects.all()
    grades = Grade.objects.filter(student=student)

    subjects_with_grades = []
    for subject in subjects:
        subject_grades = grades.filter(subject=subject)
        subjects_with_grades.append({"subject": subject, "grades": subject_grades})

    context = {
        "student": student,
        "team": team,
        "subjects_with_grades": subjects_with_grades,
    }

    return render(request, "my_grades.html", context)
