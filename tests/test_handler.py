import sys


sys.path.insert(0, "/home/robertd/projetos/tech-challenge-lambda/src")

from cpf_validator.handler import handler


def test_handler_valid_cpf():
    result = handler({"cpf": "12345678909"}, None)
    assert result == {"valid": True}


def test_handler_invalid_cpf():
    result = handler({"cpf": "12345678900"}, None)
    assert result == {"valid": False}


def test_handler_cpf_with_mask():
    result = handler({"cpf": "123.456.789-09"}, None)
    assert result == {"valid": True}


def test_handler_missing_cpf_field():
    result = handler({}, None)
    assert result == {"valid": False}


def test_handler_cpf_none():
    result = handler({"cpf": None}, None)
    assert result == {"valid": False}


def test_handler_non_dict_event():
    result = handler("not a dict", None)
    assert result == {"valid": False}


def test_handler_empty_event():
    result = handler({}, None)
    assert result == {"valid": False}
