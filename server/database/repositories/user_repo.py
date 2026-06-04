from bcrypt import checkpw
from typing import Any, Optional
from .base_repo import BaseRepository

class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями"""
    
    async def exists(self, username: str) -> bool:
        """Проверка существования пользователя"""
        row = await self.fetch_one(
            "SELECT 1 FROM users WHERE username = ?",
            (username,)
        )
        return row is not None
    
    async def create(
        self,
        username: str,
        display_name: str, 
        public_key: bytes,
        password_hash: bytes
    ) -> bool:
        """Создание нового пользователя"""
        try:
            await self.execute_query(
                "INSERT INTO users (username, display_name, public_key, password_hash) VALUES (?,?,?,?)",
                (username, display_name, public_key, password_hash)
            )
            await self.commit()
            return True
        except Exception:
            await self.rollback()
            return False
    
    async def update_display_name(self, username: str, display_name: str) -> bool:
        """Обновление публичного имени пользователя"""
        try:
            cursor = await self.conn.execute(
                "UPDATE users SET display_name = ? WHERE username = ?",
                (display_name, username)
            )
            await self.conn.commit()
            return cursor.rowcount > 0
        except Exception:
            await self.conn.rollback()
            return False
    
    async def verify_password(self, username: str, password: str) -> bool: # Плохо, надо вынести проверку
        """Проверка пароля пользователя"""
        row = await self.fetch_one(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        if not row:
            return False
        return checkpw(password.encode(), row["password_hash"])
    
    async def get_public_info(self, usernames: list[str]) -> dict[str, dict[str, Any]]:
        """Получение публичной информации о пользователях, кроме public_key"""
        placeholders = ",".join("?" for _ in usernames)
        query = f"SELECT username, display_name FROM users WHERE username IN ({placeholders})"
        rows = await self.fetch_all(query, tuple(usernames))
        
        result = {}
        for row in rows:
            result[row["username"]] = {
                "display_name": row["display_name"]
            }
        return result
    
    async def get_public_key(self, username: str) -> Optional[bytes]:
        """Получение публичного ключа пользователя"""
        row = await self.fetch_one(
            "SELECT public_key FROM users WHERE username = ?",
            (username,)
        )
        return row["public_key"] if row else None
    
    async def search(self, query: str, limit: int = 5) -> list[dict]:
        """Поиск пользователей"""
        rows = await self.fetch_all(
            "SELECT username, display_name FROM users WHERE username LIKE ? ORDER BY username LIMIT ?",
            (f"{query}%", limit)
        )   
        return [
            {
                "username": row["username"],
                "display_name": row["display_name"]
            }
            for row in rows
        ]
