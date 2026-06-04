from core.crypto.identity import Identity
from core.transport.http.api import Api
from .session_manager import SessionManager

class AuthManager:
    """Отвечает за регистрацию и аутентификацию пользователей"""
    def __init__(self, username: str, api: Api, session_manager: SessionManager):
        self.username = username
        self.api = api
        self.ssn_mngr = session_manager

#___РЕГИСТРАЦИЯ_НОВОГО_ПОЛЬЗОВАТЕЛЯ________________________________________________________________
    async def register(self, display_name: str, password: str) -> bool:
        """Регистрирует нового пользователя"""
        temp_identity = Identity.generate()
        public_key = temp_identity.public_key.public_bytes_raw()
        if not await self.api.auth.register(self.username, display_name, password, public_key):
            return False
        await self.ssn_mngr.init_storage()
        if not await self.ssn_mngr.save_identity(temp_identity.private_key.private_bytes_raw()):
            await self.ssn_mngr.close_storage()
            return False
        await self.ssn_mngr.db.identity.save_display_name(display_name)
        return True

#___АУТЕНТИФИКАЦИЯ_СУЩЕСТВУЮЩЕГО_ПОЛЬЗОВАТЕЛЯ______________________________________________________
    async def login(self, password: str) -> str | None:
        """Аутентифицирует существующего пользователя"""
        auth_token = await self.api.auth.login(self.username, password)
        if not auth_token:
            return False
        await self.ssn_mngr.init_storage()
        if not await self.ssn_mngr.load_identity():
            await self.ssn_mngr.close_storage
            return None
        return auth_token
