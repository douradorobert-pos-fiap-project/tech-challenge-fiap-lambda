import sys


sys.path.insert(0, "/home/robertd/projetos/tech-challenge-lambda/src")

from cpf_validator.validator import validate_cpf


def test_valid_cpf_without_mask():
    assert validate_cpf("12345678909") == True


def test_valid_cpf_with_mask():
    assert validate_cpf("123.456.789-09") == True


def test_invalid_cpf_wrong_first_digit():
    assert validate_cpf("12345678900") == False


def test_invalid_cpf_wrong_second_digit():
    assert validate_cpf("12345678901") == False


def test_cpf_too_short():
    assert validate_cpf("1234567890") == False


def test_cpf_too_long():
    assert validate_cpf("123456789091") == False


def test_cpf_non_numeric():
    assert validate_cpf("abcdefghijk") == False


def test_cpf_all_same_digits():
    assert validate_cpf("11111111111") == False
    assert validate_cpf("00000000000") == False
    assert validate_cpf("22222222222") == False


def test_cpf_none():
    assert validate_cpf(None) == False


def test_cpf_empty_string():
    assert validate_cpf("") == False


def test_cpf_only_digits_and_punctuation():
    assert validate_cpf("123.456.789-") == False
    assert validate_cpf(".123.456.789") == False
