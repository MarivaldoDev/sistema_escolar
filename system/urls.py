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
        "teams/<int:team_id>/subjects/<int:subject_id>/students/<int:student_id>/grade/update/",
        teacher_views.update_grade,
        name="update_grade",
    ),
    path(
        "teams/<int:team_id>/subjects/<int:subject_id>/students/<int:student_id>/grade/update/<int:bimonthly_id>/",
        teacher_views.update_grade,
        name="update_grade",
    ),
    path(
        "alunos/minhas_notas/<int:student_id>/",
        student_views.my_grades,
        name="my_grades",
    ),
    path(
        "alunos/minhas_notas/<int:student_id>/<int:subject_id>/detail/",
        student_views.grade_details,
        name="grade_details",
    ),
    path(
        "alunos/minhas_faltas/<int:student_id>/",
        student_views.my_fouls,
        name="my_fouls",
    ),
    path(
        "turma/<int:team_id>/chamada/<int:subject_id>/",
        teacher_views.fazer_chamada,
        name="fazer_chamada",
    ),
    path(
        "create_notification/", teacher_views.enviar_avisos, name="create_notification"
    ),
    path("list_notifications/", student_views.list_notifications, name="list_notifications"),
    path(
        "mark_notifications_as_read/",
        general_views.mark_notifications_as_read,
        name="mark_notifications_as_read",
    ),
    path(
        "acesso_negado/<str:mensagem>/",
        general_views.acesso_negado,
        name="acesso_negado",
    ),
]
