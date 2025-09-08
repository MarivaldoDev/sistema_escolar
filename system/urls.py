from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.my_login, name="login"),
    path("logout/", views.my_logout, name="logout"),
    path("turmas/", views.turmas, name="turmas"),
    path("turmas/<int:team_id>/", views.turma_detail, name="turma_detail"),
]
