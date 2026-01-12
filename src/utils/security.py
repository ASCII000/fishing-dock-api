"""
Security handler for the application
"""

import jwt
from datetime import datetime, timedelta, timezone


class SecurityHandler:
    """
    Handler for security
    """

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"

    def encode_payload(self, payload: dict, expires_in: int) -> str:
        """
        Generate JWT token

        Args:
            payload (dict): Payload of token
            expires_in (int): Expiration time in seconds
        """
        now = datetime.now(tz=timezone.utc)

        payload = payload.copy()
        payload.update({
            "iat": now,
            "exp": now + timedelta(seconds=expires_in),
        })

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

    def decode_payload(self, token: str) -> dict:
        """
        Decode JWT token
        """
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm]
        )

    def validate_token(self, token: str) -> bool:
        """
        Validate JWT token
        """
        try:
            self.decode_payload(token)
            return True
        except jwt.InvalidTokenError:
            return False
