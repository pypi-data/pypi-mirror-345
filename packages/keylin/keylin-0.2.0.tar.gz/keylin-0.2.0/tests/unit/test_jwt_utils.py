import jwt

from keylin.config import settings
from keylin.jwt_utils import create_jwt_for_user


# This test requires JWT_SECRET to be set, so we use the set_jwt_secret fixture.
def test_jwt_creation_and_decoding(set_jwt_secret):
    token = create_jwt_for_user(user_id=123, email="testuser@example.com")
    decoded = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    assert decoded["email"] == "testuser@example.com"
    assert decoded["sub"] == "123"
