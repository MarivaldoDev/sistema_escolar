import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from system.models import Bimonthly, CustomUser, Subject, Team


class Command(BaseCommand):
    help = "Popula o banco com alunos, professores, turmas e matérias"

    def handle(self, *args, **kwargs):
        # ==== Professores ====
        professores = []
        for i in range(1, 6):
            prof = CustomUser.objects.create_user(
                registration_number=f"P{i:03d}",
                first_name=f"Professor{i}",
                last_name="Silva",
                email=f"professor{i}@escola.com",
                password="Abc123@00",
                role="professor",
            )
            professores.append(prof)
        self.stdout.write(self.style.SUCCESS("✅ Professores criados."))

        # ==== Alunos ====
        alunos = []
        for i in range(1, 21):
            aluno = CustomUser.objects.create_user(
                registration_number=f"A{i:03d}",
                first_name=f"Aluno{i}",
                last_name="Souza",
                email=f"aluno{i}@escola.com",
                password="Abc123@00",
                role="aluno",
            )
            alunos.append(aluno)
        self.stdout.write(self.style.SUCCESS("✅ Alunos criados."))

        # ==== Turmas ====
        turmas = []
        for ano in range(2025, 2027):
            for t in range(1, 3):
                turma = Team.objects.create(name=f"Turma {t} - {ano}", year=ano)
                turma.members.set(random.sample(alunos, k=10))  # 10 alunos por turma
                turmas.append(turma)
        self.stdout.write(self.style.SUCCESS("✅ Turmas criadas."))

        # ==== Matérias ====
        nomes_materias = ["Matemática", "Português", "História", "Geografia", "Inglês"]
        for turma in turmas:
            for nome in nomes_materias:
                Subject.objects.create(
                    name=nome,
                    teacher=random.choice(professores),
                    team=turma,
                )
        self.stdout.write(self.style.SUCCESS("✅ Matérias criadas."))

        # ==== Bimestres ====
        ano_atual = timezone.now().year
        for num in range(1, 5):
            Bimonthly.objects.get_or_create(number=num, year=ano_atual)
        self.stdout.write(self.style.SUCCESS("✅ Bimestres criados."))

        self.stdout.write(self.style.SUCCESS("🎉 População concluída!"))
