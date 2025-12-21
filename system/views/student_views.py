import logging
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from system.decorators.decorators import aluno_only, aluno_required
from system.models import AttendanceRecord, CustomUser, Grade, Subject, Team
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


@login_required(login_url="login")
@aluno_only
@aluno_required
def my_fouls(request, student_id: int):
    student = get_object_or_404(CustomUser, id=student_id)
    team = Team.objects.filter(members=student).first()
    subjects = team.subjects.all() if team else Subject.objects.none()

    subject_pk = request.GET.get("subject")
    month_str = request.GET.get("month")

    fouls_qs = (
        AttendanceRecord.objects.filter(student=student, present=False)
        .select_related("attendance__subject")
        .order_by("attendance__date")
    )

    if subject_pk:
        fouls_qs = fouls_qs.filter(attendance__subject_id=subject_pk)

    if month_str:
        try:
            dt = datetime.strptime(month_str, "%Y-%m")
            fouls_qs = fouls_qs.filter(
                attendance__date__year=dt.year, attendance__date__month=dt.month
            )
        except ValueError:
            pass

    context = {
        "student": student,
        "subjects": subjects,
        "fouls": fouls_qs,
        "fouls_count": fouls_qs.count(),
        "selected_subject": subject_pk or "",
        "selected_month": month_str or "",
    }

    return render(request, "my_fouls.html", context)
