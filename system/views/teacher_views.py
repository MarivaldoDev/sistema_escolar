from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from system.forms import GradeForm, GradeUpdateForm
from system.models import CustomUser, Subject, Team


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
        # Mostra só as turmas em que o professor leciona
        turmas = Team.objects.filter(subjects__teachers=user).distinct()
    else:
        # Admin ou superuser vê todas
        turmas = Team.objects.all()

    return render(request, "turmas.html", {"turmas": turmas})


def turma_detail(request, team_id: int, subject_id: int):
    user = request.user
    turma = get_object_or_404(Team, id=team_id)

    if user.role == "professor" and not user.is_superuser:
        subject = get_object_or_404(turma.subjects.filter(teachers=user), id=subject_id)
    else:
        subject = get_object_or_404(turma.subjects, id=subject_id)

    return render(
        request,
        "turma_detail.html",
        {"turma": turma, "subject": subject},
    )


def add_grade(request, team_id: int, subject_id: int, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = get_object_or_404(Team, id=team_id)
    subject = get_object_or_404(Subject, id=subject_id)

    if student not in team.members.all():
        return redirect("turma_detail", team_id=team_id)

    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.subject = subject
            grade.team = team
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
