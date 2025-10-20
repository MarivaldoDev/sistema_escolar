import pytest

from ... import models
from ...models import CustomUser


@pytest.mark.django_db
def test_save_define_username_e_chama_send_welcome_email(monkeypatch):
    calls = []

    def fake_send_welcome(first_name, email, registration_number):
        calls.append((first_name, email, registration_number))

    # Patchar a função de envio de email no módulo models
    monkeypatch.setattr(models, "send_welcome_email", fake_send_welcome)

    registration = "A1234567"
    user = CustomUser(
        first_name="Ana",
        last_name="Maria",
        email="ana@example.com",
        registration_number=registration,
        role="aluno",
    )
    # garantir username vazio para forçar geração
    user.username = ""
    user.save()

    assert user.username == f"user_{registration}"
    assert len(calls) == 1
    assert calls[0] == ("Ana", "ana@example.com", registration)
    assert models.CustomUser.objects.filter(registration_number=registration).exists()


@pytest.mark.django_db
def test_save_gera_registration_number_quando_ausente_e_trata_colisao(monkeypatch):
    # sequência controlada: primeiro valor colide, segundo é único
    seq = ["R0000001", "R0000002"]

    def fake_generate():
        return seq.pop(0)

    monkeypatch.setattr(models, "generate_unique_registration_number", fake_generate)
    # evitar side effect de envio de email
    monkeypatch.setattr(models, "send_welcome_email", lambda *a, **k: None)

    # criar usuário existente que usará o primeiro valor (causando colisão)
    models.CustomUser.objects.create(
        first_name="Existente",
        last_name="Usuario",
        email="existente@example.com",
        registration_number="R0000001",
        role="aluno",
        password="irrelevante",
    )

    new_user = CustomUser(
        first_name="Bruno",
        last_name="Costa",
        email="bruno@example.com",
        role="aluno",
    )
    new_user.registration_number = ""
    new_user.username = ""
    new_user.save()

    # De acordo com a implementação: username é gerado usando o primeiro valor produzido,
    # depois a lógica de colisão gera um novo registration_number (o segundo valor).
    assert new_user.registration_number == "R0000002"
    assert new_user.username == "user_R0000002"
    assert models.CustomUser.objects.filter(registration_number="R0000002").exists()


@pytest.mark.django_db
def test_excecao_em_send_welcome_email_eh_suprimida(monkeypatch):
    def raising_send(*args, **kwargs):
        raise RuntimeError("falha simulada no envio")

    monkeypatch.setattr(models, "send_welcome_email", raising_send)

    user = CustomUser(
        first_name="Carlos",
        last_name="Oliveira",
        email="carlos@example.com",
        registration_number="C7654321",
        role="aluno",
    )
    # salvar não deve propagar a exceção do envio de email
    user.save()

    assert models.CustomUser.objects.filter(registration_number="C7654321").exists()
