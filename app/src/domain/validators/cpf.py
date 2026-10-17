"""Validation and normalization rules for Brazilian CPF numbers."""

import re


def _check_digit(digits: str) -> str:
    weight = len(digits) + 1
    total = sum(int(digit) * (weight - index) for index, digit in enumerate(digits))
    remainder = (total * 10) % 11
    return str(remainder % 10)


def normalize_cpf(value: str) -> str:
    """Strip punctuation and validate the CPF check digits."""
    normalized = re.sub(r"[\s.-]", "", value)
    if not re.fullmatch(r"\d{11}", normalized) or normalized == normalized[0] * 11:
        raise ValueError("CPF must be a valid Brazilian CPF")
    first = _check_digit(normalized[:9])
    second = _check_digit(normalized[:9] + first)
    if normalized[9:] != first + second:
        raise ValueError("CPF must be a valid Brazilian CPF")
    return normalized
