from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.my_login, name="login"),
    path("logout/", views.my_logout, name="logout"),
    path("turmas/", views.turmas, name="turmas"),
    path("turmas/<int:team_id>/", views.turma_detail, name="turma_detail"),
    path(
        "turmas/<int:team_id>/add_grade/<str:subject_name>/<int:student_id>/",
        views.add_grade,
        name="add_grade",
    ),
]
