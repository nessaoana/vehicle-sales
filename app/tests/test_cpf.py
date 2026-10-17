import pytest

from src.domain.validators.cpf import normalize_cpf


@pytest.mark.parametrize("value", ["52998224725", "529.982.247-25", " 529 982 247 25 "])
def test_normalize_cpf_accepts_valid_cpf_with_or_without_punctuation(value: str) -> None:
    assert normalize_cpf(value) == "52998224725"


@pytest.mark.parametrize(
    "value",
    ["52998224724", "12345678900", "11111111111", "5299822472", "529982247250", "abc.def.ghi-jk"],
)
def test_normalize_cpf_rejects_invalid_cpf(value: str) -> None:
    with pytest.raises(ValueError):
        normalize_cpf(value)
