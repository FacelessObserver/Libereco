from base64 import b64decode
from datetime import datetime, timezone
from .session_manager import SessionManager
from core.crypto.crypto import Crypt

class MessageManager:
    """Отвечает за обработку входящих сообщений: дешифровка + сохранение"""
    def __init__(self, crypt: Crypt, session_manager: SessionManager):
        self.crypt = crypt
        self.ssn_mngr = session_manager

#___ОБРАБОТКА_СООБЩЕНИЙ____________________________________________________________________________
    async def process(self, message: dict, include_text: bool) -> int | tuple[int, str, str, str] | None:
        """Обработка сообщений дешифровка + сохранение"""
        message_id = message.get("message_id")
        sender = message.get("sender")
        encrypted_b64 = message.get("encrypted_content")
        
        if message_id is None or sender is None or encrypted_b64 is None:
            return None
        
        try:
            encrypted = b64decode(encrypted_b64)
        except Exception:
            return None
        
        shared_secret = await self.ssn_mngr.get_session_key(sender)
        if not shared_secret:
            if not await self.ssn_mngr.ensure_session(sender):
                return None
            shared_secret = await self.ssn_mngr.get_session_key(sender)
        
        try:
            content = self.crypt.decrypt(encrypted, shared_secret)
        except Exception:
            return None
        
        received_at = message.get("received_at") or datetime.now(timezone.utc).isoformat()

        await self.ssn_mngr.db.messages.save(
            sender = sender,
            recipient = self.ssn_mngr.username,
            content = content,
            received_at = received_at
        )

        if include_text:
            try:
                text = content.decode()
            except UnicodeDecodeError:
                text = "[бинарные данные]"
            return message_id, sender, text, received_at
        return message_id
