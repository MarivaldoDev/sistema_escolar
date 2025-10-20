import pytest

from ...models import CustomUser


@pytest.mark.django_db
def test_create_user_requires_registration_and_email():
    manager = CustomUser.objects
    with pytest.raises(ValueError):
        manager.create_user(registration_number=None, email="a@b.com", password="p")
    with pytest.raises(ValueError):
        manager.create_user(registration_number="R1234567", email=None, password="p")


@pytest.mark.django_db
def test_create_user_creates_and_hashes_password_and_normalizes_email():
    manager = CustomUser.objects
    reg = "U0000001"
    raw_password = "Secret123!"
    mixed_email = "User@ExAMPle.Com"
    user = manager.create_user(
        registration_number=reg,
        email=mixed_email,
        password=raw_password,
        first_name="Teste",
        last_name="Usuário",
        role="aluno",
    )

    # usuário salvo
    assert CustomUser.objects.filter(registration_number=reg).exists()
    # email normalizado pelo manager (domínio em lowercase)
    expected_email = CustomUser.objects.normalize_email(mixed_email)
    assert user.email == expected_email
    # senha armazenada e verificada por check_password
    assert user.check_password(raw_password)
    # campos obrigatórios presentes
    assert user.first_name == "Teste"
    assert user.role == "aluno"


@pytest.mark.django_db
def test_create_superuser_sets_flags_and_allows_email_none():
    manager = CustomUser.objects
    reg = "S0000001"
    su = manager.create_superuser(
        registration_number=reg, email=None, password="su_pwd"
    )
    assert su.is_staff is True
    assert su.is_superuser is True
    assert su.email == ""
    assert CustomUser.objects.filter(registration_number=reg).exists()


@pytest.mark.django_db
def test_create_superuser_raises_if_flags_override_invalid():
    manager = CustomUser.objects
    # quando is_staff explicitamente False deve levantar ValueError
    with pytest.raises(ValueError):
        manager.create_superuser(
            registration_number="S0000002",
            email="su@example.com",
            password="p",
            is_staff=False,
        )
    # quando is_superuser explicitamente False deve levantar ValueError
    with pytest.raises(ValueError):
        manager.create_superuser(
            registration_number="S0000003",
            email="su2@example.com",
            password="p",
            is_superuser=False,
        )
