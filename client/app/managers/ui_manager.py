from typing import Any
from .session_manager import SessionManager
from core.transport.http.api import Api

class UIManager:
    """Отвечает за предоставление данных UI для отображения чатов и сообщений"""
    def __init__(self, username: str, session_manager: SessionManager, api: Api):
        self.username = username
        self.ssn_mngr = session_manager
        self.api = api

#___ПОЛУЧЕНИЕ_ЧАТОВ________________________________________________________________________________
    async def get_chats(self) -> list[dict[str, str]]:
        """Возвращает список чатов, отсортированный по времени последнего сообщения"""
        if self.ssn_mngr.db is None:
            return []
        
        interlocutors = await self.ssn_mngr.get_users_with_sessions()
        if not interlocutors:
            return []
        
        users_info = await self.api.users.display_info(interlocutors)
        if users_info is None:
            users_info = {}

        chats: list[dict] = []

        for interlocutor in interlocutors:
            user_info = users_info.get(interlocutor)
            display_name = user_info.get("display_name", interlocutor) if user_info else interlocutor
            
            last_message_info = await self.ssn_mngr.db.messages.get_last(interlocutor)
            if last_message_info is None:
                sender = None
                content = None
                last_time = None
            else:
                sender = last_message_info.get("sender")
                try:
                    content = last_message_info.get("content").decode()
                except:
                    content = "[бинарные данные]"
                last_time = last_message_info.get("received_at")
            
            chats.append({
                "username": interlocutor,
                "display_name": display_name,
                "is_from_me": sender != interlocutor,
                "last_message": content,
                "time": last_time
            })

        chats.sort(key = lambda x: x["time"] or "", reverse = True)
        return chats

#___ПОЛУЧЕНИЕ_СООБЩЕНИЙ________________________________________________________________________________
    async def get_chat_messages(self, interlocutor: str) -> list[dict[str, Any]]:
        """Возвращает все сообщения с собеседником"""
        if self.ssn_mngr.db is None:
            return []
        
        messages = await self.ssn_mngr.db.messages.get(interlocutor)
        result = []
        for message in messages:
            try:
                text = message.get("content").decode()
            except:
                text = "[бинарные данные]"
            result.append({
                "is_from_me": message.get("sender") == self.username,
                "message": text,
                "time": message.get("received_at"),
            })
        return result
