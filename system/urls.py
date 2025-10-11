from django.urls import path

from system.views import general_views, student_views, teacher_views

urlpatterns = [
    path("", general_views.home, name="home"),
    path("login/", general_views.my_login, name="login"),
    path("logout/", general_views.my_logout, name="logout"),
    path("search/", general_views.search, name="search"),
    path("turmas/", teacher_views.turmas, name="turmas"),
    path(
        "turmas/<int:team_id>/escolher-materia/",
        teacher_views.escolher_materia,
        name="escolher_materia",
    ),
    path(
        "turmas/<int:team_id>/<int:subject_id>/",
        teacher_views.turma_detail,
        name="turma_detail",
    ),
    path(
        "turmas/<int:team_id>/add_grade/<int:subject_id>/<int:student_id>/",
        teacher_views.add_grade,
        name="add_grade",
    ),
    path(
        "turmas/<int:team_id>/update_grade/<int:subject_id>/<int:student_id>/",
        teacher_views.update_grade,
        name="update_grade",
    ),
    path(
        "alunos/minhas_notas/<int:student_id>/",
        student_views.my_grades,
        name="my_grades",
    ),
    path('turma/<int:team_id>/chamada/<int:subject_id>/', teacher_views.fazer_chamada, name='fazer_chamada'),
]
