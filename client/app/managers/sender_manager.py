from uuid import uuid4
from .chat_manager import ChatManager
from .session_manager import SessionManager
from core.crypto.crypto import Crypt
from core.transport.websocket.ws_client import WebSocketClient

class SenderManager:
    """Отвечает за шифрование и отправку исходящих сообщений"""
    def __init__(self, username: str, crypt: Crypt, session_manager: SessionManager,
                 chat_manager: ChatManager, ws: WebSocketClient):
        self.username = username
        self.crypt = crypt
        self.ssn_mngr = session_manager
        self.chat_mngr = chat_manager
        self.ws = ws

        self.pending: dict[str, dict] = {}

#___ОТПРАВКА_СООБЩЕНИЙ_В_ЗАШИФРОВАНОМ_ВИДЕ_________________________________________________________
    async def send_message(self, recipient: str, data: bytes) -> bool:
        """Отправляет сообщение пользователю в зашифрованном виде"""
        if not self.ws.is_authenticated:
            return False
        
        shared_secret = await self.ssn_mngr.get_session_key(recipient)
        if shared_secret is None:
            if not await self.ssn_mngr.ensure_session(recipient):
                return False
            await self.ws.create_chat(recipient)
            shared_secret = await self.ssn_mngr.get_session_key(recipient)
            if shared_secret is None:
                return False
        
        encrypted = self.crypt.encrypt(data, shared_secret)

        temp_id = uuid4().hex
        self.pending[temp_id] = {"recipient": recipient, "data": data}

        if not await self.ws.send_message(temp_id, recipient, encrypted):
            del self.pending[temp_id]
            return False
        return True
