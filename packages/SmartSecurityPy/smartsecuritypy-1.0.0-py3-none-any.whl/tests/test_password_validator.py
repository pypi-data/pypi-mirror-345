import pytest
from SmartSecurityPy.password_validator import PasswordValidator, PasswordStrength

@pytest.fixture
def validator():
    return PasswordValidator()

def test_empty_password(validator):
    result = validator.validate_password("")
    assert result.score == 0
    assert "A senha não pode estar vazia" in result.feedback
    assert not result.is_strong

def test_weak_password(validator):
    result = validator.validate_password("123")
    assert result.score < 70
    assert not result.is_strong
    assert len(result.feedback) > 0

def test_strong_password(validator):
    result = validator.validate_password("P@ssw0rd123!")
    assert result.score >= 70
    assert result.is_strong
    assert len(result.feedback) <= 2

def test_common_password(validator):
    result = validator.validate_password("password")
    assert result.score < 70
    assert not result.is_strong
    assert "Esta senha é muito comum" in result.feedback

def test_password_with_sequence(validator):
    result = validator.validate_password("abc123")
    assert result.score < 70
    assert not result.is_strong
    assert "sequências de caracteres" in result.feedback

def test_password_with_repetition(validator):
    result = validator.validate_password("aaa123")
    assert result.score < 70
    assert not result.is_strong
    assert "repetições de caracteres" in result.feedback

def test_password_suggestions(validator):
    suggestions = validator.get_password_suggestions("weak")
    assert len(suggestions) > 0
    assert any("maiúscula" in s for s in suggestions)
    assert any("número" in s for s in suggestions)

def test_password_length_scoring(validator):
    # Testa pontuação para diferentes comprimentos
    short_pass = validator.validate_password("Abc1!")
    long_pass = validator.validate_password("Abc1!Def2@Ghi3#")
    
    assert short_pass.score < long_pass.score
    assert "pelo menos 8 caracteres" in short_pass.feedback

def test_password_complexity_scoring(validator):
    # Testa pontuação para diferentes níveis de complexidade
    simple_pass = validator.validate_password("password123")
    complex_pass = validator.validate_password("P@ssw0rd123!")
    
    assert simple_pass.score < complex_pass.score
    assert complex_pass.is_strong

def test_password_strength_edge_cases(validator):
    # Testa casos limite
    result = validator.validate_password("A" * 100)  # Senha muito longa
    assert result.score > 0
    assert "repetições de caracteres" in result.feedback

    result = validator.validate_password("!@#$%^&*()")  # Apenas caracteres especiais
    assert result.score < 70
    assert not result.is_strong
    assert any("número" in s for s in result.feedback) 