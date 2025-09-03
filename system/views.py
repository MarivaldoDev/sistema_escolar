from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib.auth import authenticate, login


def my_login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    form = LoginForm(request.POST)
    if form.is_valid():
        registration_number = form.cleaned_data['registration_number']
        password = form.cleaned_data['password']
        user = authenticate(request, registration_number=registration_number, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html', {'form': form})


def home(request):
    return render(request, 'home.html')