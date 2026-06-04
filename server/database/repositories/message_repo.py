from datetime import datetime, timezone
from base64 import b64encode
from typing import Optional, Tuple
from .base_repo import BaseRepository

class MessageRepository(BaseRepository):
    """Репозиторий для работы с сообщениями"""
    
    async def save(
        self,
        sender: str,
        recipient: str, 
        encrypted_content: bytes
        ) -> Tuple[Optional[int], Optional[str]]:
        """Сохранение сообщения"""
        received_at = datetime.now(timezone.utc).isoformat()
        try:
            cursor = await self.execute_query(
                "INSERT INTO messages (sender, recipient, encrypted_content, received_at) VALUES (?, ?, ?, ?)",
                (sender, recipient, encrypted_content, received_at)
            )
            await self.commit()
            return cursor.lastrowid, received_at
        except Exception:
            await self.rollback()
            return None, None
    
    async def get(self, username: str) -> list[dict]:
        """Получение сообщений пользователя"""
        rows = await self.fetch_all(
            "SELECT id, sender, encrypted_content, received_at FROM messages WHERE recipient = ? ORDER BY received_at ASC",
            (username,)
        )
        
        return [
            {
                "message_id": row["id"],
                "sender": row["sender"],
                "encrypted_content": b64encode(row["encrypted_content"]).decode(),
                "received_at": row["received_at"]
            }
            for row in rows
        ]
    
    async def delete(self, message_ids: list[int], recipient: str) -> None:
        """Удаление сообщений"""
        try:
            placeholders = ",".join("?" for _ in message_ids)
            query = f"DELETE FROM messages WHERE id IN ({placeholders}) AND recipient = ?"
            await self.execute_query(query, message_ids + [recipient])
            await self.commit()
        except Exception:
            await self.rollback()
