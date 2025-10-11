import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from system.forms import GradeForm, GradeUpdateForm
from system.models import (Attendance, AttendanceRecord, CustomUser, Grade,
                           Subject, Team)
from system.utiuls.functions import is_aproved


def escolher_materia(request, team_id: int):
    user = request.user
    turma = get_object_or_404(Team, id=team_id)

    if user.role == "professor" and not user.is_superuser:
        subjects = turma.subjects.filter(teachers=user)
    else:
        subjects = turma.subjects.all()

    if subjects.count() > 1:
        return render(
            request,
            "escolher_materia.html",
            {"turma": turma, "subjects": subjects},
        )
    elif subjects.count() == 1:
        subject = subjects.first()
        return redirect("turma_detail", team_id=team_id, subject_id=subject.id)
    else:
        return HttpResponse("Nenhuma matéria disponível para esta turma.")


def turmas(request):
    user = request.user

    if user.role == "professor" and not user.is_superuser:
        turmas = Team.objects.filter(subjects__teachers=user).distinct()
    else:
        turmas = Team.objects.all()

    return render(request, "turmas.html", {"turmas": turmas})


def turma_detail(request, team_id: int, subject_id: int):
    user = request.user
    turma = get_object_or_404(Team, id=team_id)

    if user.role == "professor" and not user.is_superuser:
        subject = get_object_or_404(turma.subjects.filter(teachers=user), id=subject_id)
    else:
        subject = get_object_or_404(turma.subjects, id=subject_id)

    alunos = turma.members.all()
    alunos_com_status = []

    for aluno in alunos:
        grades_qs = Grade.objects.filter(
            student=aluno, subject=subject, team=turma
        ).order_by("bimonthly__number")

        grades = [g.value for g in grades_qs]
        bimonthlys = [str(g.bimonthly) for g in grades_qs]

        if grades:
            aprovado = is_aproved(grades, bimonthlys)
            aluno.status = "aprovado" if aprovado else "reprovado"
        else:
            aluno.status = "reprovado"

        alunos_com_status.append(aluno)

    return render(
        request,
        "turma_detail.html",
        {
            "turma": turma,
            "subject": subject,
            "alunos": alunos_com_status,
            "bimonthlys": len(bimonthlys),
        },
    )


def add_grade(request, team_id: int, subject_id: int, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

    # Garante que o aluno realmente pertence à turma
    if student not in team.members.all():
        return redirect("turma_detail", team_id=team_id, subject_id=subject_id)

    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.subject = subject
            grade.team = team

            # Verifica se já existe uma nota lançada para o mesmo bimestre
            existing_grade = Grade.objects.filter(
                student=student, subject=subject, team=team, bimonthly=grade.bimonthly
            ).first()

            if existing_grade:
                # Atualiza o valor da nota existente
                existing_grade.value = grade.value
                existing_grade.save()
            else:
                # Cria uma nova nota
                grade.save()

            return redirect("turma_detail", team_id=team_id, subject_id=subject_id)
    else:
        form = GradeForm()

    return render(
        request,
        "add_grade.html",
        {"form": form, "student": student, "subject": subject, "team": team},
    )


def update_grade(request, team_id: int, subject_id: int, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

    if student not in team.members.all():
        return redirect("turma_detail", team_id=team_id)

    grade_instance = student.grade_set.filter(subject=subject).first()

    if request.method == "POST":
        form = GradeUpdateForm(request.POST, instance=grade_instance)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.subject = subject
            grade.save()
            return redirect("turma_detail", team_id=team_id, subject_id=subject_id)
    else:
        form = GradeUpdateForm(instance=grade_instance)

    return render(
        request,
        "update_grade.html",
        {"form": form, "student": student, "subject": subject, "team": team},
    )


def fazer_chamada(request, team_id: int, subject_id: int):
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)
    alunos = team.members.all()

    # Se o professor já fez a chamada hoje, mostramos o registro existente
    attendance, created = Attendance.objects.get_or_create(
        teacher=request.user,
        team=team,
        subject=subject,
        date__exact=datetime.date.today(),
    )

    if request.method == "POST":
        for aluno in alunos:
            presente = request.POST.get(f"presente_{aluno.id}") == "on"
            AttendanceRecord.objects.update_or_create(
                attendance=attendance, student=aluno, defaults={"present": presente}
            )
        return redirect("turma_detail", team_id=team.id, subject_id=subject.id)

    registros_existentes = {r.student_id: r.present for r in attendance.records.all()}

    return render(
        request,
        "chamada.html",
        {
            "team": team,
            "subject": subject,
            "alunos": alunos,
            "registros": registros_existentes,
        },
    )
