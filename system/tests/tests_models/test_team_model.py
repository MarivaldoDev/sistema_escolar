import pytest
from django.core.exceptions import ValidationError

from ...models import CustomUser, Team


@pytest.mark.django_db
def test_str_method():
    team = Team.objects.create(name="TDS A", year=2025)
    assert str(team) == "TDS A - 2025"


@pytest.mark.django_db
def test_apenas_alunos_na_turma():
    aluno = CustomUser.objects.create(
        first_name="Pedro",
        last_name="Silva",
        email="aluno@example.com",
        registration_number="A1234567",
        role="aluno",
        password="teste123",
    )
    team = Team.objects.create(name="TDS A", year=2025)
    team.members.add(aluno)

    assert aluno in team.members.all()
    assert team in aluno.teams.all()


@pytest.mark.django_db
def test_professor_nao_pode_ser_membro():
    """Garante que professores não podem ser adicionados à turma."""
    professor = CustomUser.objects.create(
        first_name="João",
        last_name="Santos",
        email="prof@example.com",
        registration_number="P7654321",
        role="professor",
        password="teste123",
    )
    team = Team.objects.create(name="1ºA", year=2025)

    team.members.add(professor)

    with pytest.raises(ValidationError):
        team.clean()


@pytest.mark.django_db
def test_filtragem_por_ano():
    turma_2025 = Team.objects.create(name="1ºA", year=2025)
    turma_24 = Team.objects.create(name="2ºB", year=2024)
    turmas_2025 = Team.objects.filter(year=2025)

    assert turma_2025 in turmas_2025
    assert turma_24 not in turmas_2025
