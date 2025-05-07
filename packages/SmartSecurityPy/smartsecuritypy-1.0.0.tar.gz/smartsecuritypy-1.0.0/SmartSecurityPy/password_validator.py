from typing import Dict, List, Tuple
import re
from dataclasses import dataclass

@dataclass
class PasswordStrength:
    score: int  # 0-100
    feedback: List[str]
    is_strong: bool

class PasswordValidator:
    def __init__(self):
        self.min_length = 8
        self.common_passwords = self._load_common_passwords()
        
    def _load_common_passwords(self) -> set:
        # Lista básica de senhas comuns - em produção, isso deveria vir de um arquivo ou banco de dados
        return {
            "password", "123456", "12345678", "qwerty", "abc123",
            "monkey", "letmein", "dragon", "111111", "baseball",
            "iloveyou", "trustno1", "sunshine", "master", "welcome",
            "shadow", "ashley", "football", "jesus", "michael"
        }

    def validate_password(self, password: str) -> PasswordStrength:
        """
        Valida a força de uma senha e retorna um objeto PasswordStrength com score e feedback.
        """
        if not password:
            return PasswordStrength(0, ["A senha não pode estar vazia"], False)

        feedback = []
        score = 0

        # Verifica comprimento
        if len(password) < self.min_length:
            feedback.append(f"pelo menos {self.min_length} caracteres")
        else:
            score += 20
            if len(password) >= 12:
                score += 10

        # Verifica complexidade
        checks = {
            r'[A-Z]': "Adicione letras maiúsculas",
            r'[a-z]': "Adicione letras minúsculas",
            r'[0-9]': "Adicione números",
            r'[^A-Za-z0-9]': "Adicione caracteres especiais"
        }

        for pattern, message in checks.items():
            if not re.search(pattern, password):
                feedback.append(message)
            else:
                score += 15

        # Verifica senhas comuns
        if password.lower() in self.common_passwords:
            feedback.append("Esta senha é muito comum")
            score = max(0, score - 30)

        # Verifica sequências
        if self._has_sequence(password):
            feedback.append("sequências de caracteres")
            score = max(0, score - 10)

        # Verifica repetições
        if self._has_repetition(password):
            feedback.append("repetições de caracteres")
            score = max(0, score - 10)

        # Determina se a senha é forte
        is_strong = score >= 70 and len(feedback) <= 2

        return PasswordStrength(score, feedback, is_strong)

    def _has_sequence(self, password: str) -> bool:
        """Verifica se a senha contém sequências comuns."""
        sequences = [
            "123", "234", "345", "456", "567", "678", "789",
            "abc", "bcd", "cde", "def", "efg", "fgh", "ghi",
            "qwe", "wer", "ert", "rty", "tyu", "yui", "uio"
        ]
        password_lower = password.lower()
        return any(seq in password_lower for seq in sequences)

    def _has_repetition(self, password: str) -> bool:
        """Verifica se a senha contém repetições de caracteres."""
        return bool(re.search(r'(.)\1{2,}', password))

    def get_password_suggestions(self, password: str) -> List[str]:
        """
        Retorna sugestões para melhorar a força da senha.
        """
        strength = self.validate_password(password)
        suggestions = []

        if not strength.is_strong:
            if len(password) < self.min_length:
                suggestions.append(f"Aumente o comprimento para pelo menos {self.min_length} caracteres")
            
            if not re.search(r'[A-Z]', password):
                suggestions.append("Adicione pelo menos uma letra maiúscula")
            
            if not re.search(r'[a-z]', password):
                suggestions.append("Adicione pelo menos uma letra minúscula")
            
            if not re.search(r'[0-9]', password):
                suggestions.append("Adicione pelo menos um número")
            
            if not re.search(r'[^A-Za-z0-9]', password):
                suggestions.append("Adicione pelo menos um caractere especial")

        return suggestions 