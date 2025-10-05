from django.shortcuts import get_object_or_404, redirect, render

from system.models import CustomUser, Grade, Team
from system.utiuls.functions import is_aproved


def my_grades(request, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)

    if request.user != student:
        return redirect("home")

    team = Team.objects.filter(members=student).first()

    if not team:
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
        # ✅ agora filtrando por student, subject e team
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
    }

    return render(request, "my_grades.html", context)
