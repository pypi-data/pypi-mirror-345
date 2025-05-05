import jwt

from keylin.config import JWT_ALGORITHM, JWT_SECRET
from keylin.jwt_utils import create_jwt_for_user


def test_jwt_creation_and_decoding():
    token = create_jwt_for_user(user_id=123, email="testuser@example.com")
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert decoded["email"] == "testuser@example.com"
    assert decoded["sub"] == "123"
