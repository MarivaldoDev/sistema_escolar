from django.shortcuts import get_object_or_404, redirect, render

from system.models import CustomUser, Grade, Team


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
    grades = Grade.objects.filter(student=student)

    subjects_with_grades = []
    for subject in subjects:
        subject_grades = grades.filter(subject=subject)
        subjects_with_grades.append({"subject": subject, "grades": subject_grades})

    context = {
        "student": student,
        "team": team,
        "subjects_with_grades": sorted(subjects_with_grades, key=lambda x: x["subject"].name),
    }

    return render(request, "my_grades.html", context)
