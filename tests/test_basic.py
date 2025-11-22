import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes import allowed_file, generate_pkce


def test_allowed_file():
    """Простой тест функции allowed_file"""
    assert allowed_file('test.xlsx') == True
    assert allowed_file('test.csv') == True
    assert allowed_file('test.txt') == False
    assert allowed_file('') == False


def test_generate_pkce():
    """Простой тест генерации PKCE"""
    code_verifier, code_challenge = generate_pkce()

    assert len(code_verifier) > 0
    assert len(code_challenge) > 0
    assert '=' not in code_challenge
    assert '+' not in code_challenge
    assert '/' not in code_challenge


def test_basic_math():
    """Простой тест для проверки работы pytest"""
    assert 1 + 1 == 2
    assert 2 * 2 == 4


# Тесты, которые не требуют контекста приложения
class TestSimpleFunctions:
    def test_string_operations(self):
        assert "hello".upper() == "HELLO"
        assert " TEST ".strip() == "TEST"