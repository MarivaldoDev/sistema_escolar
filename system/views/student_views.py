import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from system.decorators.decorators import aluno_only, aluno_required
from system.models import CustomUser, Grade, Subject, Team
from system.utiuls.functions import is_aproved

logger = logging.getLogger(__name__)


@login_required(login_url="login")
@aluno_only
@aluno_required
def my_grades(request, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = Team.objects.filter(members=student).first()

    if not team:
        logger.warning(f"Aluno {student.first_name} não está associado a nenhuma turma")
        return render(
            request,
            "my_grades.html",
            {
                "student": student,
                "team": None,
                "subjects_with_grades": [],
            },
        )

    subjects = team.subjects.all()
    subjects_with_grades = []
    max_bimonthlys = 0

    for subject in subjects:
        subject_grades = Grade.objects.filter(
            student=student, subject=subject, team=team
        ).order_by("bimonthly__number")

        grade_values = [g.average for g in subject_grades]
        bimonthlys = [str(g.bimonthly) for g in subject_grades]
        if len(bimonthlys) > max_bimonthlys:
            max_bimonthlys = len(bimonthlys)

        if grade_values:
            aprovado = is_aproved(grade_values, bimonthlys)
            media = sum(grade_values) / len(grade_values)
        else:
            aprovado = False
            media = None

        subjects_with_grades.append(
            {
                "subject": subject,
                "grades": subject_grades,
                "status": "Aprovado" if aprovado else "Reprovado",
                "media": media,
            }
        )

    context = {
        "student": student,
        "team": team,
        "subjects_with_grades": sorted(
            subjects_with_grades, key=lambda x: x["subject"].name
        ),
        "bimonthlys": max_bimonthlys,
    }

    return render(request, "my_grades.html", context)


@login_required(login_url="login")
@aluno_only
@aluno_required
def grade_details(request, student_id: int, subject_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    subject = get_object_or_404(Subject, id=subject_id)

    qs = (
        Grade.objects.filter(student=student, subject=subject)
        .select_related("bimonthly")
        .order_by("bimonthly__number")
    )

    performances = [
        {
            "bimonthly": str(g.bimonthly),
            "activity": g.value_activity,
            "proof": g.value_proof,
            "average": g.average,
        }
        for g in qs
    ]

    context = {
        "student": student,
        "subject": subject,
        "performances": performances,
    }

    return render(request, "grade_details.html", context)

