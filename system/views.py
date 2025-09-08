from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm
from .models import Team


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
    turmas = Team.objects.all()
    return render(request, "turmas.html", {"turmas": turmas})


def turma_detail(request, team_id: int):
    turma = get_object_or_404(Team, id=team_id)
    return render(request, "turma_detail.html", {"turma": turma})
