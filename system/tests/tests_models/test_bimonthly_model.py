import pytest

from ...models import Bimonthly


@pytest.mark.django_db
def test_str_method():
    bimonthly = Bimonthly.objects.create(number=2, year=2024)
    assert str(bimonthly) == "2º Bimestre/2024"
