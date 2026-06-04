from .connection import DatabaseConnection
from .migrations import DatabaseMigrations
from .repositories.identity_repo import IdentityRepository
from .repositories.session_repo import SessionRepository
from .repositories.message_repo import MessageRepository

class Database:
    """Фасад для работы с базой данных"""

    def __init__(self, username: str):
        self._connection = DatabaseConnection(f"{username}.db")
        self._identity_repo = None
        self._session_repo = None
        self._message_repo = None

    async def init(self):
        """Инициализация базы данных"""
        conn = await self._connection.connect()
        await DatabaseMigrations.create_tables(conn)

        self._identity_repo = IdentityRepository(conn)
        self._session_repo = SessionRepository(conn)
        self._message_repo = MessageRepository(conn)

    async def close(self):
        """Закрытие соединения"""
        await self._connection.close()

    @property
    def identity(self) -> IdentityRepository:
        return self._identity_repo

    @property
    def sessions(self) -> SessionRepository:
        return self._session_repo

    @property
    def messages(self) -> MessageRepository:
        return self._message_repo
