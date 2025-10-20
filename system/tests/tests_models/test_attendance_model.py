import pytest

from ...models import Attendance, CustomUser, Subject, Team


@pytest.mark.django_db
def test_str_method():
    professor = CustomUser.objects.create(
        first_name="João",
        last_name="Santos",
        email="prof@example.com",
        registration_number="P7654321",
        role="professor",
        password="teste123",
    )
    team = Team.objects.create(name="TDS A", year=2025)
    subject = Subject.objects.create(name="Matemática")
    attendance = Attendance.objects.create(
        teacher=professor,
        team=team,
        subject=subject,
    )

    assert str(attendance) == f"Chamada - TDS A / Matemática ({attendance.date})"
