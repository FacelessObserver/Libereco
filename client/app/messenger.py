from datetime import datetime, timezone
from typing import Callable, Any

from core.crypto.crypto import Crypt
from core.transport.http.api import Api
from core.transport.websocket.ws_client import WebSocketClient

from .managers.auth_manager import AuthManager
from .managers.chat_manager import ChatManager
from .managers.message_manager import MessageManager
from .managers.sender_manager import SenderManager
from .managers.session_manager import SessionManager
from .managers.sync_manager import SyncManager
from .managers.ui_manager import UIManager

class Messenger:
    """Клиент мессенджера"""
    def __init__(self, username, server_url: str = "http://127.0.0.1:8000"):
        self.username = username
        self.server_url = server_url
        self.ws_url = server_url.replace("http://", "ws://").replace("https://", "wss://")

        self.crypt = Crypt()
        self.api = Api(self.server_url, verify_ssl = False)
        self.ws = WebSocketClient(self.ws_url)

        self.auth_token: str | None = None
        self.is_logged_in: bool = False

        self.ssn_mngr = SessionManager(self.username, self.api)
        self.auth_mngr = AuthManager(self.username, self.api, self.ssn_mngr)
        self.chat_mngr = ChatManager()
        self.msg_mngr = MessageManager(self.crypt, self.ssn_mngr)
        self.sndr_mngr = SenderManager(self.username, self.crypt, self.ssn_mngr, self.chat_mngr, self.ws)
        self.sync_mngr = SyncManager(self.api, self.ssn_mngr, self.msg_mngr)
        self.ui_mngr = UIManager(self.username, self.ssn_mngr, self.api)

        self.on_message_callback: Callable[[str, str, str], Any] | None = None
        self.on_connect_callback: Callable[[], Any] | None = None
        self.on_disconnect_callback: Callable[[int | None, str], Any] | None = None
        self.on_sync_complete_callback: Callable[[], Any] | None = None

#___ВЫХОД_ИЗ_ПРИЛОЖЕНИЯ____________________________________________________________________________
    async def close(self) -> None:
        """Закрывает подключение и освобождает ресурсы"""
        if self.ws:
            await self.ws.disconnect()
        await self.ssn_mngr.close_storage()
        if self.api:
            await self.api.http.close_cli()

#___РЕГИСТРАЦИЯ_И_АУТЕНТИФИКАЦИЯ___________________________________________________________________
    async def register(self, display_name: str, password: str) -> bool:
        return await self.auth_mngr.register(display_name, password)
    
    async def login(self, password: str) -> bool:
        auth_token = await self.auth_mngr.login(password)
        if not auth_token:
            return False
        self.auth_token = auth_token
        self.is_logged_in = True
        return True

#___WEBSOCKET______________________________________________________________________________________
    @property
    def is_connected(self) -> bool:
        return self.ws.is_connected

    async def connect(self) -> bool:
        if not self.is_logged_in or not self.auth_token:
            return False
        if self.is_connected:
            return True
        
        self.ws.on_connect_callback = self._on_ws_connect
        self.ws.on_disconnect_callback = self._on_ws_disconnect
        self.ws.on_error_callback = self._on_ws_error
        self.ws.on_message_callback = self._on_ws_message_from_user
        self.ws.on_message_status_callback = self._on_message_receive_status
        self.ws.on_new_chat_callback = self._on_new_chat

        if await self.ws.connect(self.username, self.auth_token):
            return True
        return False
    
    async def disconnect(self) -> None:
        await self.ws.disconnect()

#___WEBSOCKET_ОБРАБОТЧИКИ__________________________________________________________________________
    async def _on_ws_connect(self) -> None:
        if self.on_connect_callback:
            self.on_connect_callback()
    
    async def _on_ws_disconnect(self, code: int | None, reason: str) -> None:
        if self.on_disconnect_callback:
            self.on_disconnect_callback(code, reason)
    
    async def _on_ws_error(self, error: Exception):
        pass # Потом добавлю логирование

    async def _on_ws_message_from_user(self, data: dict) -> None:
        result = await self.msg_mngr.process(data, include_text = True)
        if result is not None:
            message_id, sender, text, received_at = result
            if self.ws.is_authenticated:
                await self.ws.send_message_delivery_confirmation(message_id)
            if self.on_message_callback:
                await self.on_message_callback(sender, text, received_at)
    
    async def _on_message_receive_status(self, data: dict) -> None:
        is_received = data.get("received", False)
        temp_id = data.get("temp_id")
        if is_received and temp_id and temp_id in self.sndr_mngr.pending:
            info = self.sndr_mngr.pending.pop(temp_id)
            await self.ssn_mngr.db.messages.save(
                self.username,
                info.get("recipient"),
                info.get("data"),
                data.get("received_at") or datetime.now(timezone.utc).isoformat()
            )

    async def _on_new_chat(self, data: dict) -> None: # ПЕРЕДЕЛАТЬ ЛОГИКУ ДЛЯ ДВУХ КЕЙСОВ
        if data.get("type") == "chat_created":
            peer = data.get("copycat")
        else:
            peer = data.get("initiator")

        if peer is None or peer == self.username:
            return
        
        await self.ssn_mngr.ensure_session(peer)
        self.chat_mngr.confirm_chat_created(peer)

        if data.get("type") != "chat_created":
            await self.ws.chat_delivery_confirmation(peer)

#___ЗАГРУЗКА_ОФФЛАЙН_ДАННЫХ________________________________________________________________________
    async def load_offline_data(self) -> None:
        await self.sync_mngr.load_offline_data(self.username)
        if self.on_sync_complete_callback:
            await self.on_sync_complete_callback()

#___ОТПРАВКА_ТЕКСТОВЫХ_СООБЩЕНИЙ___________________________________________________________________
    async def send_text_message(self, recipient: str, text: str) -> bool:
        return await self.sndr_mngr.send_message(recipient, text.encode())


#___UI_МЕТОДЫ______________________________________________________________________________________
    async def get_chats(self) -> list[dict]:
        return await self.ui_mngr.get_chats()

    async def get_chat_messages(self, interlocutor: str) -> list[dict]:
        return await self.ui_mngr.get_chat_messages(interlocutor)


#___КОЛЛБЭКИ_______________________________________________________________________________________
    def set_on_message(self, callback: Callable[[str, str, str], Any]) -> None:
        self.on_message_callback = callback
    
    def set_on_connect(self, callback: Callable[[], Any]) -> None:
        self.on_connect_callback = callback
    
    def set_on_disconnect(self, callback: Callable[[int | None, str], Any]) -> None:
        self.on_disconnect_callback = callback

    def set_on_sync_complete(self, callback: Callable[[], Any]) -> None:
        self.on_sync_complete_callback = callback
