from core.crypto.identity import Identity
from core.database.database import Database
from core.transport.http.api import Api

class SessionManager:
    """Отвечает за операции с идентичностью и сессиями"""
    def __init__(self, username: str, api: Api):
        self.username = username
        self.api = api
        self.db: Database | None = None
        self.identity: Identity | None = None

#___УПРАВЛЕНИЕ_ХРАНИЛИЩЕМ__________________________________________________________________________
    async def init_storage(self) -> None:
        """Инициализирует локальное хранилище, если оно не открыто"""
        if self.db is None:
            self.db = Database(self.username)
            await self.db.init()

    async def close_storage(self) -> None:
        """Закрывает локальное хранилище и освобождает ресурсы"""
        if self.db:
            await self.db.close()
            self.db = None

#___ИДЕНТИЧНОСТЬ___________________________________________________________________________________
    async def save_identity(self, private_bytes: bytes) -> bool:
        """Сохраняет приватный ключ в локальном хранилище"""
        if not self.db:
            return False
        return await self.db.identity.save(private_bytes)

    async def load_identity(self) -> Identity | None:
        """Загружает приватный ключ из хранилища и создает объект Identity"""
        if self.db is None:
            return None
        private_bytes = await self.db.identity.get()
        if private_bytes is None:
            return None
        self.identity = Identity.from_bytes(private_bytes)
        return self.identity

#___СЕССИИ_________________________________________________________________________________________
    async def session_exists(self, interlocutor: str) -> bool:
        """Проверяет, есть ли сессия с собеседником в локальном хранилище"""
        if self.db is None:
            return False
        return await self.db.sessions.exists(interlocutor)

    async def _create_and_save_session(self, interlocutor: str, public_key: bytes) -> bool:
        """Вычисляет общий секрет и сохраняет его в локальном хранилище"""
        shared_secret = self.identity.shared_secret(public_key)
        return await self.db.sessions.save(interlocutor, shared_secret)
    
    async def save_session(self, interlocutor: str, public_key: bytes) -> bool:
        """Сохраняет сессию на основе публичного ключа собеседника"""
        if self.db is None or self.identity is None:
            return False
        return await self._create_and_save_session(interlocutor, public_key)

    async def ensure_session(self, interlocutor: str) -> bool:
        """Гарантирует наличие общей сессии с собеседником"""
        if not self.db:
            return False
        if await self.db.sessions.exists(interlocutor):
            return True
        if not self.identity:
            return False
        public_key = await self.api.users.public_key(interlocutor)
        if not public_key:
            return False
        return await self._create_and_save_session(interlocutor, public_key)
    
    async def get_session_key(self, interlocutor: str) -> bytes | None:
        """Возвращает общий секрет с собеседником из локального хранилища"""
        if self.db is None:
            return None
        return await self.db.sessions.get_secret(interlocutor)
    
    async def get_users_with_sessions(self) -> list[str]:
        """Список всех пользователей, с которыми есть общий секрет"""
        if self.db is None:
            return []
        return await self.db.sessions.get_sessions()
