from base64 import b64decode
from .message_manager import MessageManager
from .session_manager import SessionManager
from core.transport.http.api import Api

class SyncManager:
    """Загружает и обрабатывает накопившиеся данные"""
    def __init__(self, api: Api, session_manager: SessionManager, message_manager: MessageManager):
        self.api = api
        self.ssn_mngr = session_manager
        self.msg_mngr = message_manager

#___ЗАГРУЗКА_->_ОБРАБОТКА_+_СОХРАНЕНИЕ_СООБЩЕНИЙ_->_ПОДТВЕРЖДЕНИЕ_ДОСТАВКИ_________________________
    async def load_offline_data(self, username: str) -> None:
        """Получает чаты/сообщения через HTTP, обрабатывает и подтверждает доставку"""
        data = await self.api.sync.sync(username)
        if data is None:
            return
        
        chat_initiators = []
        message_ids = []
        
        for chat in data.get("chats", []):
            initiator = chat.get("initiator_username")
            public_key_b64 = chat.get("public_key")
            if initiator is None or public_key_b64 is None:
                continue
            try:
                public_key = b64decode(public_key_b64)
            except Exception:
                continue

            if not await self.ssn_mngr.session_exists(initiator):
                await self.ssn_mngr.save_session(initiator, public_key)
            
            chat_initiators.append(initiator)

        for message in data.get("messages", []):
            message_id = await self.msg_mngr.process(message, False)
            if message_id is not None:
                message_ids.append(message_id)
        
        if message_ids or chat_initiators:
            await self.api.sync.ack(username, message_ids, chat_initiators)
