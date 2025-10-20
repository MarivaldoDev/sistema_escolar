import pytest

from ...models import Attendance, AttendanceRecord, CustomUser, Subject, Team


@pytest.mark.django_db
def test_method_str():
    aluno = CustomUser.objects.create(
        first_name="Pedro",
        last_name="Silva",
        email="aluno@example.com",
        registration_number="A1234567",
        role="aluno",
        password="teste123",
    )

    team = Team.objects.create(name="TDS A", year=2025)

    professor = CustomUser.objects.create(
        first_name="João",
        last_name="Santos",
        email="prof@example.com",
        registration_number="P7654321",
        role="professor",
        password="teste123",
    )

    subject = Subject.objects.create(name="Matemática")
    attendance = Attendance.objects.create(
        teacher=professor, team=team, subject=subject
    )

    attendance_record = AttendanceRecord.objects.create(
        attendance=attendance, student=aluno, present=True
    )

    assert str(attendance_record) == "Pedro - Presente"
