from .base_repo import BaseRepository
from typing import Optional

class SessionRepository(BaseRepository):
    """Репозиторий для работы с сессиями"""

    async def exists(self, interlocutor: str) -> bool:
        """Проверка существования сессии"""
        row = await self.fetch_one(
            "SELECT 1 FROM sessions WHERE interlocutor = ?",
            (interlocutor,)
        )
        return row is not None

    async def save(self, interlocutor: str, shared_secret: bytes) -> bool:
        """Сохранение сессии"""
        try:
            await self.execute(
                "INSERT OR REPLACE INTO sessions (interlocutor, shared_secret) VALUES (?, ?)",
                (interlocutor, shared_secret)
            )
            await self.commit()
            return True
        except Exception:
            return False

    async def get_secret(self, interlocutor: str) -> Optional[bytes]:
        """Получение общего секрета"""
        row = await self.fetch_one(
            "SELECT shared_secret FROM sessions WHERE interlocutor = ?",
            (interlocutor,)
        )
        return row["shared_secret"] if row else None

    async def get_sessions(self) -> list[str]:
        """Получение списка всех пользователей, с кем установлена сессия"""
        rows = await self.fetch_all(
            "SELECT interlocutor FROM sessions ORDER BY interlocutor",
            ()
        )
        return [row["interlocutor"] for row in rows]
