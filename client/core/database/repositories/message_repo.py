from typing import Any, Optional
from .base_repo import BaseRepository

class MessageRepository(BaseRepository):
    """Репозиторий для работы с сообщениями"""

    async def save(
        self,
        sender: str,
        recipient: str,
        content: bytes,
        received_at: str
    ) -> bool:
        """Сохранение сообщения"""
        try:
            await self.execute(
                "INSERT INTO messages (sender, recipient, content, received_at) VALUES (?,?,?,?)",
                (sender, recipient, content, received_at)
            )
            await self.commit()
            return True
        except Exception:
            return False

    async def get(self, interlocutor: str) -> list[dict]:
        """Получение сообщений с пользователем"""
        rows = await self.fetch_all(
            "SELECT * FROM messages WHERE sender = ? OR recipient = ? ORDER BY received_at ASC",
            (interlocutor, interlocutor)
        )
        return [
            {
                "sender": row["sender"],
                "recipient": row["recipient"],
                "content": row["content"],
                "received_at": row["received_at"]
            }
            for row in rows
        ]

    async def get_last(self, interlocutor: str) -> Optional[dict[str, Any]]:
        """Получение последнего сообщения с пользователем"""
        row = await self.fetch_one(
            """SELECT sender, content, received_at FROM messages
               WHERE sender = ? OR recipient = ?
               ORDER BY received_at DESC LIMIT 1""",
            (interlocutor, interlocutor)
        )
        if row is None:
            return None
        return {
            "sender": row["sender"],
            "content": row["content"],
            "received_at": row["received_at"]
        }
