from aiosqlite import Connection
from typing import Optional

class BaseRepository:
    """Базовый класс для всех репозиториев"""
    
    def __init__(self, conn: Connection):
        self.conn = conn
    
    async def execute_query(self, query: str, params: Optional[tuple]):
        """Выполнение запроса"""
        cursor = await self.conn.execute(query, params or ())
        return cursor
    
    async def fetch_one(self, query: str, params: tuple):
        """Получение одной записи"""
        cursor = await self.execute_query(query, params)
        return await cursor.fetchone()
    
    async def fetch_all(self, query: str, params: tuple):
        """Получение всех записей"""
        cursor = await self.execute_query(query, params)
        return await cursor.fetchall()
    
    async def commit(self):
        """Подтверждение изменений"""
        await self.conn.commit()
    
    async def rollback(self):
        """Откат изменений"""
        await self.conn.rollback()
