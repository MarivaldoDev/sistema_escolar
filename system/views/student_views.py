import logging

from django.shortcuts import get_object_or_404, redirect, render

from system.models import CustomUser, Grade, Team
from system.utiuls.functions import is_aproved

logger = logging.getLogger(__name__)


def my_grades(request, student_id: int):
    user = request.user
    student = get_object_or_404(CustomUser, id=student_id)

    if user != student:
        logger.warning(
            f"Professor {request.user.first_name} tentou acessar as notas de um aluno"
        )
        return redirect("acesso_negado", user_role=user.role)

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

    for subject in subjects:
        subject_grades = Grade.objects.filter(
            student=student, subject=subject, team=team
        ).order_by("bimonthly__number")

        grade_values = [g.value for g in subject_grades]
        bimonthlys = [str(g.bimonthly) for g in subject_grades]

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
        "bimonthlys": len(bimonthlys),
    }

    return render(request, "my_grades.html", context)
