import pytest
from django.urls import reverse

from ...models import CustomUser


@pytest.mark.django_db
def test_view_home(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert "home.html" in (t.name for t in response.templates)


@pytest.mark.django_db
def test_view_login_get(client):
    response = client.get(reverse("login"))
    print(response.context)

    assert response.status_code == 200
    assert "login.html" in (t.name for t in response.templates)
    assert "form" in response.context


@pytest.mark.django_db
def test_view_login_post_valid(client):
    senha = "teste123"
    aluno = CustomUser.objects.create_user(
        first_name="Pedro",
        last_name="Silva",
        email="aluno@example.com",
        registration_number="A1234567",
        role="aluno",
        password=senha,
    )
    response = client.post(
        reverse("login"),
        {"registration_number": aluno.registration_number, "password": senha},
    )

    assert response.status_code == 302
    assert response.url == reverse("home")


@pytest.mark.django_db
def test_view_login_post_invalid(client):
    senha = "teste123"
    aluno = CustomUser.objects.create_user(
        first_name="Pedro",
        last_name="Silva",
        email="aluno@example.com",
        registration_number="A1234567",
        role="aluno",
        password=senha,
    )
    response = client.post(
        reverse("login"),
        {"registration_number": aluno.registration_number, "password": "senha_errada"},
    )

    assert response.status_code == 200
    assert "login.html" in (t.name for t in response.templates)
    assert "form" in response.context
    messages = list(response.context["messages"])
    assert any("inválido" in m.message.lower() for m in messages)


@pytest.mark.django_db
def test_view_login_post_campo_vazio(client):
    senha = "teste123"
    aluno = CustomUser.objects.create_user(
        first_name="Pedro",
        last_name="Silva",
        email="aluno@example.com",
        registration_number="A1234567",
        role="aluno",
        password=senha,
    )
    response = client.post(
        reverse("login"),
        {"registration_number": aluno.registration_number, "password": ""},
    )

    assert response.status_code == 200
    assert "login.html" in (t.name for t in response.templates)
    assert "form" in response.context
    assert response.context["form"].errors


def test_logout_view(client):
    response = client.get(reverse("logout"))

    assert response.status_code == 302
    assert response.url == reverse("login")
