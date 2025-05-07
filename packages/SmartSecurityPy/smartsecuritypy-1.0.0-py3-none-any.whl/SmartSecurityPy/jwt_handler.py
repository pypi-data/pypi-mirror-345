import jwt
from datetime import datetime, timedelta
from typing import Any, Dict

# Exemplo de chave secreta segura
SECRET_KEY = "minha_chave_supersecreta"
ALGORITHM = "HS256"


def create_token(data: Dict[str, Any], expires_in_minutes: int = 60) -> str:
    """Cria um JWT com expiração."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decodifica um JWT e retorna os dados."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def is_token_valid(token: str) -> bool:
    """Verifica se o token é válido (assinatura e expiração)."""
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
