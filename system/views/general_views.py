from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import LoginForm
from ..models import CustomUser, Grade, Team


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
    else:
        for error in form.errors:
            messages.error(request, form.errors[error])
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
            "subjects_with_grades": sorted(
                subjects_with_grades, key=lambda x: x["subject"].name
            ),
            "search_value": search_value,
        },
    )
