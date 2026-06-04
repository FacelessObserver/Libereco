from datetime import datetime, timedelta, timezone
from jose import jwt
from .config import JWT_ALGORITHM, JWT_SECRET

class Auth:
    def __init__(self, secret = JWT_SECRET, algorithm = JWT_ALGORITHM):
        self.secret = secret
        self.algorithm = algorithm
    
    def create_access_token(
            self,
            username: str,
        )-> str:
        """Генерация JWT-токена"""
        expire = datetime.now(timezone.utc) + timedelta(hours = 2)
        payload = {
            "sub": username,
            "exp": expire
        }
        return jwt.encode(
            claims = payload,
            key = self.secret,
            algorithm = self.algorithm
        )
    
    def verify_token(self, token: str, expected_username: str) -> bool:
        """Проверка JWT-токена"""
        try:
            payload = jwt.decode(token, self.secret, algorithms = [self.algorithm])
            return payload.get("sub") == expected_username
        except Exception:
            return False
