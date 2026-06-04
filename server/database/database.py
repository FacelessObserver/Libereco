from typing import Optional
from .connection import DatabaseConnection
from .migrations import DatabaseMigrations
from .repositories.user_repo import UserRepository
from .repositories.chat_repo import ChatRepository
from .repositories.message_repo import MessageRepository

class Database:
    """Фасад для работы с базой данных"""
    
    def __init__(self, db_path: Optional[str]):
        self.connection_manager = DatabaseConnection(db_path)
        self._user_repo = None
        self._chat_repo = None
        self._message_repo = None
    
    async def init(self):
        """Инициализация базы данных"""
        conn = await self.connection_manager.connect()
        await DatabaseMigrations.init(conn)
        
        self._user_repo = UserRepository(conn)
        self._chat_repo = ChatRepository(conn)
        self._message_repo = MessageRepository(conn)
    
    async def close(self):
        """Закрытие соединения"""
        await self.connection_manager.close()
        
    @property
    def users(self) -> UserRepository:
        return self._user_repo
    
    @property
    def chats(self) -> ChatRepository:
        return self._chat_repo
    
    @property
    def messages(self) -> MessageRepository:
        return self._message_repo
