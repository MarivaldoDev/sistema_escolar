from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.my_login, name="login"),
    path("logout/", views.my_logout, name="logout"),
    path("search/", views.search, name="search"),
    path("turmas/", views.turmas, name="turmas"),
    path(
        "turmas/<int:team_id>/<int:subject_id>/",
        views.turma_detail,
        name="turma_detail",
    ),
    path(
        "turmas/<int:team_id>/add_grade/<int:subject_id>/<int:student_id>/",
        views.add_grade,
        name="add_grade",
    ),
    path(
        "turmas/<int:team_id>/update_grade/<int:subject_id>/<int:student_id>/",
        views.update_grade,
        name="update_grade",
    ),
    path("alunos/minhas_notas/<int:student_id>/", views.my_grades, name="my_grades"),
]
