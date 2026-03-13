import jwt
import datetime
from typing import Optional

SECRET_KEY = "my-secret-hw-key"
ALGORITHM = "HS256"

class AuthService:
    def create_token(self, account_id: int) -> str:
        payload = {
            "sub": str(account_id),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload["sub"])
        except (jwt.PyJWTError, ValueError):
            return None

auth_service = AuthService()