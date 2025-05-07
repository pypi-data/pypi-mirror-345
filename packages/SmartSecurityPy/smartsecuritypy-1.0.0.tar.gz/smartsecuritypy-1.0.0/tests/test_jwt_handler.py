from SmartSecurityPy import jwt_handler
import time

def test_create_and_decode_token():
    data = {"user_id": 123, "role": "admin"}
    token = jwt_handler.create_token(data, expires_in_minutes=1)

    decoded = jwt_handler.decode_token(token)

    assert decoded["user_id"] == 123
    assert decoded["role"] == "admin"
    assert "exp" in decoded

def test_token_validation():
    token = jwt_handler.create_token({"valid": True}, expires_in_minutes=1)
    assert jwt_handler.is_token_valid(token) is True

    # Token expirado
    short_token = jwt_handler.create_token({"exp_test": True}, expires_in_minutes=0)
    time.sleep(1)  # garante expiração
    assert jwt_handler.is_token_valid(short_token) is False
