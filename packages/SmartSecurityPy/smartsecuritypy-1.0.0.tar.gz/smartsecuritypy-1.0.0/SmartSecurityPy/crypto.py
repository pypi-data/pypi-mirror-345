from cryptography.fernet import Fernet

# Função para gerar chave secreta
# Obs: guarde isso com segurança!
def generate_key() -> bytes:
    return Fernet.generate_key()

def encrypt_message(message: str, key: bytes) -> str:
    """Criptografa uma mensagem com uma chave."""
    fernet = Fernet(key)
    return fernet.encrypt(message.encode()).decode()

def decrypt_message(token: str, key: bytes) -> str:
    """Descriptografa uma mensagem criptografada com a chave."""
    fernet = Fernet(key)
    return fernet.decrypt(token.encode()).decode()
