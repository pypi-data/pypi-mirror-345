from SmartSecurityPy.crypto import generate_key, encrypt_message, decrypt_message

def test_encrypt_and_decrypt_message():
    key = generate_key()
    message = "mensagem secreta"

    encrypted = encrypt_message(message, key)
    decrypted = decrypt_message(encrypted, key)

    assert isinstance(encrypted, str)
    assert encrypted != message
    assert decrypted == message
