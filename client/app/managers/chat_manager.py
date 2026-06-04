from asyncio import Event, TimeoutError, wait_for
from core.transport.websocket.ws_client import WebSocketClient

class ChatManager:
    """Отвечает за создание чатов"""
    def __init__(self):
        self.pending: dict[str, Event] = {}

#___СОЗДАНИЕ_ЧАТА_С_ПОЛЬЗОВАТЕЛЕМ__________________________________________________________________
    async def create_chat(self, copycat: str, ws: WebSocketClient) -> bool:
        """Создает чат с пользователем"""
        if not ws.is_authenticated:
            return False
        
        if copycat in self.pending:
            event = self.pending[copycat]
            try:
                await wait_for(event.wait(), timeout = 5.0)
                return True
            except TimeoutError:
                del self.pending[copycat]
                return False
        
        event = Event()
        self.pending[copycat] = event
        if not await ws.create_chat(copycat):
            del self.pending[copycat]
            return False
        try:
            await wait_for(event.wait(), timeout = 5.0)
        except TimeoutError:
            del self.pending[copycat]
            return False

#___ПОДТВЕРЖДЕНИЕ_СОЗДАНИЯ_ЧАТА____________________________________________________________________
    def confirm_chat_created(self, copycat: str) -> None:
        """Подтверждает создание чата с пользователем"""
        if copycat in self.pending:
            self.pending.pop(copycat).set()
