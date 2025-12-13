import pytest
from django.core.exceptions import ValidationError

from ...models import Bimonthly, CustomUser, Grade, Subject, Team


@pytest.mark.django_db
def test_str_method():
    aluno = CustomUser.objects.create(
        first_name="Pedro",
        last_name="Silva",
        email="aluno@example.com",
        registration_number="A1234567",
        role="aluno",
        password="teste123",
    )

    team = Team.objects.create(name="TDS A", year=2025)
    subject = Subject.objects.create(name="Programação")
    bimonthly = Bimonthly.objects.create(number=1, year=2025)
    grade = Grade.objects.create(
        student=aluno,
        subject=subject,
        team=team,
        value_activity=9.0,
        value_proof=9.5,
        bimonthly=bimonthly,
    )

    assert str(grade) == "Pedro Silva (1º Bimestre/2025) - Programação: 9.25"


@pytest.mark.django_db
def test_nota_menor_que_zero():
    aluno = CustomUser.objects.create(
        first_name="Pedro",
        last_name="Silva",
        email="aluno@example.com",
        registration_number="A1234567",
        role="aluno",
        password="teste123",
    )

    team = Team.objects.create(name="TDS A", year=2025)
    subject = Subject.objects.create(name="Programação")
    bimonthly = Bimonthly.objects.create(number=1, year=2025)
    grade = Grade.objects.create(
        student=aluno,
        subject=subject,
        team=team,
        value_activity=-1.0,
        value_proof=-1.0,
        bimonthly=bimonthly,
    )

    with pytest.raises(ValidationError):
        grade.clean()


@pytest.mark.django_db
def test_nota_maior_que_dez():
    aluno = CustomUser.objects.create(
        first_name="Pedro",
        last_name="Silva",
        email="aluno@example.com",
        registration_number="A1234567",
        role="aluno",
        password="teste123",
    )

    team = Team.objects.create(name="TDS A", year=2025)
    subject = Subject.objects.create(name="Programação")
    bimonthly = Bimonthly.objects.create(number=1, year=2025)
    grade = Grade.objects.create(
        student=aluno,
        subject=subject,
        team=team,
        value_activity=11.0,
        value_proof=11.0,
        bimonthly=bimonthly,
    )

    with pytest.raises(ValidationError):
        grade.clean()
