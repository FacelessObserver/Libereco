from base64 import b64encode
from .base_repo import BaseRepository

class ChatRepository(BaseRepository):
    """Репозиторий для работы с чатами"""
    
    async def exists(self, user1: str, user2: str) -> bool:
        """Проверка существования чата"""
        row = await self.fetch_one(
            "SELECT 1 FROM chats WHERE (initiator = ? AND copycat = ?) OR (initiator = ? AND copycat = ?)",
            (user1, user2, user2, user1)
        )
        return row is not None
    
    async def create(self, initiator: str, copycat: str) -> bool:
        """Создание чата"""
        if initiator == copycat:
            return False
        
        try:
            await self.execute_query(
                "INSERT INTO chats (initiator, copycat) VALUES (?, ?)",
                (initiator, copycat)
            )
            await self.commit()
            return True
        except Exception:
            await self.rollback()
            return False
    
    async def delete(self, copycat: str, initiators: list[str]) -> None:
        """Удаление чатов, где пользователь - copycat"""
        try:
            placeholders = ",".join("?" for _ in initiators)
            query = f"DELETE FROM chats WHERE copycat = ? AND initiator IN ({placeholders})"
            await self.execute_query(query, [copycat] + initiators)
            await self.commit()
        except Exception:
            await self.rollback()
    
    async def get(self, username: str) -> list[dict]:
        """Получение всей публичной информации о пользователях, которые инициировали чат"""
        rows = await self.fetch_all(
            """SELECT
                c.initiator AS initiator_username,
                u.display_name AS initiator_display_name,
                u.public_key AS initiator_public_key
            FROM chats c
            LEFT JOIN users u ON u.username = c.initiator
            WHERE c.copycat = ?""",
            (username,)
        )
        return [
            {
                "initiator_username": row["initiator_username"],
                "display_name": row["initiator_display_name"],
                "public_key": b64encode(row["initiator_public_key"]).decode()
            }
            for row in rows
        ]
