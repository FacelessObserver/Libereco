from aiosqlite import Connection

class BaseRepository:
    """Базовый класс для всех репозиториев"""
    
    def __init__(self, conn: Connection):
        self.conn = conn

    async def execute(self, query: str, params: tuple):
        return await self.conn.execute(query, params)

    async def fetch_one(self, query: str, params: tuple):
        cursor = await self.conn.execute(query, params)
        return await cursor.fetchone()

    async def fetch_all(self, query: str, params: tuple):
        cursor = await self.conn.execute(query, params)
        return await cursor.fetchall()

    async def commit(self):
        await self.conn.commit()
