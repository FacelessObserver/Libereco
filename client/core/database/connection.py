import aiosqlite
from typing import Optional

class DatabaseConnection:

    def __init__(self, path: str):
        self.db_path = path
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> aiosqlite.Connection:
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row        
        return self.conn

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def __aenter__(self):
        return await self.connect()
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
