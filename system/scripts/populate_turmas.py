import random

from django.utils import timezone

from system.models import CustomUser, Team
from system.utiuls.functions import generate_unique_registration_number


def run():
    year = timezone.now().year

    # Criar 100 alunos se ainda não existirem
    total_alunos = CustomUser.objects.filter(role="aluno").count()
    alunos = []

    if total_alunos < 100:
        for i in range(100 - total_alunos):
            print("Criando aluno", i + 1)
            reg_num = generate_unique_registration_number()
            aluno = CustomUser.objects.create_user(
                registration_number=reg_num,
                first_name=f"Aluno{i+1}",
                last_name="Teste",
                email=f"aluno{i+1}@exemplo.com",
                password="Abc123@00",
                role="aluno",
            )
            alunos.append(aluno)
        print(f"Criados {len(alunos)} alunos novos.")
    else:
        alunos = list(CustomUser.objects.filter(role="aluno")[:100])

    # Criar 5 turmas
    for i in range(1, 6):
        team, created = Team.objects.get_or_create(name=f"Turma {i}", year=year)
        if created:
            print(f"Turma {team.name} criada.")
        # Adiciona 20 alunos aleatórios à turma
        selected_students = random.sample(alunos, 20)
        team.members.set(selected_students)
        team.save()

    print("✅ 5 turmas criadas com 20 alunos cada.")
