import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from system.forms import GradeForm, GradeUpdateForm
from system.models import (Attendance, AttendanceRecord, Bimonthly, CustomUser,
                           Grade, Subject, Team)
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
        ).order_by("student")

        grades = [g.value for g in grades_qs]
        bimonthlys = [str(g.bimonthly) for g in grades_qs]

        if grades:
            aprovado = is_aproved(grades, bimonthlys)
            aluno.status = "aprovado" if aprovado else "reprovado"
        else:
            aluno.status = "reprovado"

        alunos_com_status.append(aluno)
        paginator = Paginator(sorted(alunos_com_status, key=lambda x: x.first_name), 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
    

    return render(
        request,
        "turma_detail.html",
        {
            "turma": turma,
            "subject": subject,
            "bimonthlys": len(bimonthlys),
            "page_obj": page_obj,
        },
    )


def add_grade(request, team_id: int, subject_id: int, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

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
                messages.error(
                    request,
                    "Já existe uma nota lançada para este bimestre. Se deseja alterá-la, utilize a opção de atualizar nota.",
                )
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


def update_grade(
    request, team_id: int, subject_id: int, student_id: int, bimonthly_id: int = None
):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

    if student not in team.members.all():
        return redirect("turma_detail", team_id=team_id, subject_id=subject_id)

    # Se nenhum bimestre foi escolhido, mostrar lista de bimestres para selecionar
    if bimonthly_id is None:
        bimonthlys = Bimonthly.objects.all().order_by("number")
        # Para exibir notas já lançadas por bimestre (se existir)
        bimestres_info = []
        for b in bimonthlys:
            g = Grade.objects.filter(
                student=student, subject=subject, team=team, bimonthly=b
            ).first()
            bimestres_info.append({"bimonthly": b, "grade": g})

        return render(
            request,
            "choose_bimonthly.html",
            {
                "student": student,
                "subject": subject,
                "team": team,
                "bimestres": bimestres_info,
            },
        )

    # Se chegou com um bimestre, carregar / criar a instância da nota daquele bimestre
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


def fazer_chamada(request, team_id: int, subject_id: int):
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)
    alunos = team.members.all()

    if request.method == "POST":
        attendance, created = Attendance.objects.get_or_create(
            teacher=request.user,
            team=team,
            subject=subject,
            date=datetime.date.today(),
        )
        for aluno in alunos:
            presente = request.POST.get(f"presente_{aluno.id}") == "on"
            AttendanceRecord.objects.update_or_create(
                attendance=attendance, student=aluno, defaults={"present": presente}
            )
        return redirect("turma_detail", team_id=team.id, subject_id=subject.id)

    attendance = Attendance.objects.filter(
        teacher=request.user,
        team=team,
        subject=subject,
        date=datetime.date.today(),
    ).first()

    if attendance is not None:
        messages.info(
            request, "Chamada já realizada hoje. Você pode atualizar os registros."
        )

    registros_existentes = {r.student_id: r.present for r in attendance.records.all()} if attendance else {}

    return render(
        request,
        "chamada.html",
        {
            "team": team,
            "subject": subject,
            "alunos": alunos.order_by("first_name"),
            "registros": registros_existentes,
        },
    )