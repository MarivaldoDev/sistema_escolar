import datetime
import logging
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from system.decorators.decorators import professor_required
from system.forms import GradeForm, GradeUpdateForm, NotificationForm
from system.models import (Attendance, AttendanceRecord, Bimonthly, CustomUser,
                           Grade, Subject, Team)
from system.utiuls.functions import is_aproved
from notifications.signals import notify


logger = logging.getLogger(__name__)


@login_required(login_url="login")
@professor_required
def escolher_materia(request, team_id: int):
    user = request.user

    turma = get_object_or_404(
        Team.objects.prefetch_related("subjects__teachers"), id=team_id
    )

    if user.role == "professor" and not user.is_superuser:
        subjects = list(turma.subjects.filter(teachers=user))
    else:
        subjects = list(turma.subjects.all())

    if not subjects:
        messages.warning(request, "Nenhuma matéria disponível para esta turma.")
        return redirect("turmas")

    if len(subjects) == 1:
        return redirect("turma_detail", team_id=team_id, subject_id=subjects[0].id)

    return render(
        request,
        "escolher_materia.html",
        {"turma": turma, "subjects": subjects},
    )


@login_required(login_url="login")
@professor_required
def turmas(request):
    user = request.user

    if user.role == "professor" and not user.is_superuser:
        turmas = (
            Team.objects.filter(subjects__teachers=user)
            .distinct()
            .prefetch_related("subjects")
        )
    else:
        turmas = Team.objects.all().prefetch_related("subjects")

    return render(request, "turmas.html", {"turmas": turmas})


@login_required(login_url="login")
@professor_required
def turma_detail(request, team_id: int, subject_id: int):
    user = request.user

    turma = get_object_or_404(Team.objects.prefetch_related("members"), id=team_id)

    if user.role == "professor" and not user.is_superuser:
        subject = get_object_or_404(turma.subjects.filter(teachers=user), id=subject_id)
    else:
        subject = get_object_or_404(turma.subjects, id=subject_id)

    alunos = list(turma.members.all())

    grades_qs = Grade.objects.filter(team=turma, subject=subject).select_related(
        "bimonthly", "student"
    )

    grades_by_student = defaultdict(list)
    for g in grades_qs:
        value = g.average
        try:
            value_float = float(value)
        except Exception:
            logger.debug(
                "Nota com valor inválido ignorada",
                extra={
                    "grade_id": getattr(g, "id", None),
                    "student_id": getattr(g.student, "id", None),
                    "raw_value": value,
                },
            )
            continue

        grades_by_student[g.student_id].append(
            {"value": value_float, "bimonthly": str(g.bimonthly)}
        )

    bimestres_all = list(Bimonthly.objects.all().order_by("number"))
    bimes_count = len(bimestres_all)

    alunos_status = []
    for aluno in alunos:
        aluno_grades_info = grades_by_student.get(aluno.id, [])
        grades_values = [item["value"] for item in aluno_grades_info]
        bimes_list = [item["bimonthly"] for item in aluno_grades_info]

        aluno.total_notas = len(grades_values)
        aluno.is_under_review = bimes_count == 4 and aluno.total_notas < 4

        if grades_values:
            try:
                aprovado = is_aproved(grades_values, bimes_list)
            except Exception as e:
                logger.error(
                    "Erro em is_aproved",
                    exc_info=True,
                    extra={
                        "student_id": aluno.id,
                        "grades_values": grades_values,
                        "bimes": bimes_list,
                    },
                )
                aprovado = False

            aluno.status = "aprovado" if aprovado else "reprovado"
        else:
            aluno.status = "reprovado"

        alunos_status.append(aluno)

    alunos_status.sort(key=lambda x: x.first_name)

    paginator = Paginator(alunos_status, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "turma_detail.html",
        {
            "turma": turma,
            "subject": subject,
            "bimonthlys": bimes_count,
            "page_obj": page_obj,
        },
    )


@login_required(login_url="login")
@professor_required
def add_grade(request, team_id: int, subject_id: int, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

    if not team.members.filter(id=student.id).exists():
        return redirect("turma_detail", team_id=team_id, subject_id=subject_id)

    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.subject = subject
            grade.team = team

            if Grade.objects.filter(
                student=student,
                subject=subject,
                team=team,
                bimonthly=grade.bimonthly,
            ).exists():
                messages.error(request, "Já existe uma nota para este bimestre.")
                return render(
                    request,
                    "add_grade.html",
                    {
                        "form": form,
                        "student": student,
                        "subject": subject,
                        "team": team,
                    },
                )

            grade.save()
            return redirect("turma_detail", team_id=team_id, subject_id=subject_id)

        for erro in form.errors.get("__all__", []):
            messages.error(request, erro)

    else:
        form = GradeForm()

    return render(
        request,
        "add_grade.html",
        {"form": form, "student": student, "subject": subject, "team": team},
    )


@login_required(login_url="login")
@professor_required
def update_grade(
    request, team_id: int, subject_id: int, student_id: int, bimonthly_id: int = None
):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

    if not team.members.filter(id=student.id).exists():
        return redirect("turma_detail", team_id=team_id, subject_id=subject_id)

    if bimonthly_id is None:
        bimestres = Bimonthly.objects.all().order_by("number")
        info = [
            {
                "bimonthly": b,
                "grade": Grade.objects.filter(
                    student=student, subject=subject, team=team, bimonthly=b
                ).first(),
            }
            for b in bimestres
        ]

        return render(
            request,
            "choose_bimonthly.html",
            {"student": student, "subject": subject, "team": team, "bimestres": info},
        )

    bimonthly = get_object_or_404(Bimonthly, id=bimonthly_id)

    grade_instance = Grade.objects.filter(
        student=student, subject=subject, team=team, bimonthly=bimonthly
    ).first()

    if request.method == "POST":
        form = GradeUpdateForm(request.POST, instance=grade_instance)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.subject = subject
            grade.team = team
            grade.bimonthly = bimonthly
            grade.save()

            return redirect("turma_detail", team_id=team_id, subject_id=subject_id)

        for erro in form.errors.get("__all__", []):
            messages.error(request, erro)

    else:
        form = GradeUpdateForm(instance=grade_instance)

    return render(
        request,
        "update_grade.html",
        {
            "form": form,
            "student": student,
            "subject": subject,
            "team": team,
            "bimonthly": bimonthly,
        },
    )


@login_required(login_url="login")
@professor_required
def fazer_chamada(request, team_id: int, subject_id: int):
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

    alunos = team.members.order_by("first_name")
    today = datetime.date.today()

    if request.method == "POST":
        attendance, _ = Attendance.objects.get_or_create(
            teacher=request.user,
            team=team,
            subject=subject,
            date=today,
        )

        for aluno in alunos:
            presente = request.POST.get(f"presente_{aluno.id}") == "on"
            AttendanceRecord.objects.update_or_create(
                attendance=attendance,
                student=aluno,
                defaults={"present": presente},
            )

        return redirect("turma_detail", team_id=team.id, subject_id=subject.id)

    attendance = (
        Attendance.objects.filter(
            teacher=request.user, team=team, subject=subject, date=today
        )
        .prefetch_related("records")
        .first()
    )

    registros = (
        {r.student_id: r.present for r in attendance.records.all()}
        if attendance
        else {}
    )

    if attendance:
        messages.info(request, "Chamada já realizada hoje. Você pode atualizar.")

    return render(
        request,
        "chamada.html",
        {
            "team": team,
            "subject": subject,
            "alunos": alunos,
            "registros": registros,
        },
    )


@login_required(login_url="login")
@professor_required
def enviar_avisos(request):
    if request.method == "POST":
        form = NotificationForm(request.POST, user=request.user)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            recipient = form.cleaned_data["recipient"]
            
            # Enviar notificação para cada membro da turma selecionada
            members = recipient.members.all() if recipient else []
            for member in members:
                notify.send(
                    sender=request.user,
                    verb=title,
                    description=content,
                    recipient=member,
                    actor=request.user,
                )

            messages.success(request, "Aviso enviado com sucesso!")
            return redirect("create_notification")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        form = NotificationForm(user=request.user)

    return render(request, "enviar_avisos.html", {"form": form})