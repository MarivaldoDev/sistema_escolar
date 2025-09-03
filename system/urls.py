from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_login, name='login'),
    path('home/', views.home, name='home'),
]