from .base_repo import BaseRepository
from typing import Optional

class IdentityRepository(BaseRepository):
    """Репозиторий для работы с идентичностями"""

    async def exists(self) -> bool:
        """Проверка существования приватного ключа"""
        row = await self.fetch_one("SELECT private_key FROM identity LIMIT 1")
        return row is not None

    async def save(self, private_key: bytes) -> bool:
        """Сохранение приватного ключа"""
        try:
            await self.execute(
                "INSERT OR REPLACE INTO identity (id, private_key) VALUES (1, ?)",
                (private_key,)
            )
            await self.commit()
            return True
        except Exception as e:
            print(e)
            return False

    async def get(self) -> Optional[bytes]:
        """Получение приватного ключа"""
        row = await self.fetch_one("SELECT private_key FROM identity LIMIT 1", ())
        return row["private_key"] if row else None
    
    async def save_display_name(self, display_name: str) -> bool:
        try:
            print(display_name)
            await self.execute(
                "UPDATE identity SET display_name = ? WHERE id = 1",
                (display_name,)
            )
            await self.commit()
            return True
        except Exception:
            return False
    
    async def get_display_name(self) -> Optional[bytes]:
        """Получение публичного имени"""
        row = await self.fetch_one("SELECT display_name FROM identity LIMIT 1", ())
        return row["display_name"] if row else None
