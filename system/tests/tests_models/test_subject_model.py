import pytest
from django.core.exceptions import ValidationError

from ...models import CustomUser, Subject, Team


@pytest.mark.django_db
def test_str_method():
    team = Team.objects.create(name="TDS A", year=2025)
    subject = Subject.objects.create(name="Matemática")
    subject.team.add(team)
    assert str(subject) == "Matemática"


@pytest.mark.django_db
def test_apenas_professores_tem_relacionamento_com_materia():
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
    subject.team.add(team)
    subject.teachers.add(professor)

    assert professor in subject.teachers.all()
    subject.teachers.add(aluno)
    with pytest.raises(ValidationError):
        subject.clean()
