from SmartSecurityPy import hasher

def test_hash_and_verify_password():
    password = "minha_senha_super_segura"
    hashed = hasher.hash_password(password)

    assert isinstance(hashed, str)
    assert hashed != password
    assert hasher.verify_password(password, hashed) is True
    assert hasher.verify_password("senha_errada", hashed) is False
