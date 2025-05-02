"""JWT utilities."""

from typing import Literal
import jwt


def get_jwt_status(
    token: str,
) -> tuple[Literal["valid", "expired", "invalid"], dict | None]:
    """
    Validate a JWT token.
    """
    try:
        decoded_token = jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": True, "verify_iat": True},
        )
        return "valid", decoded_token
    except jwt.ExpiredSignatureError:
        # Signature has expired
        return "expired", None
    except jwt.InvalidTokenError:
        # Token is invalid
        return "invalid", None
