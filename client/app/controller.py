from asyncio import create_task
from datetime import datetime, timezone
from typing import Any, Callable
from .messenger import Messenger

class AppController:
    def __init__(self):
        self.messenger: Messenger | None = None
        self._current_username: str | None = None
        self._current_display_name: str | None = None

        self._on_message_callback: Callable[[str, str, str], Any] | None = None
        self._on_connect_callback: Callable[[], Any] | None = None
        self._on_disconnect_callback: Callable[[int | None, str], Any] | None = None
        self._on_sync_complete_callback: Callable[[], Any] | None = None

        self._display_names_cache: dict[str, str] = {}

    def _apply_callbacks(self) -> None:
        if self.messenger is None:
            return
        if self._on_message_callback:
            self.messenger.set_on_message(self._on_message_callback)
        if self._on_connect_callback:
            self.messenger.set_on_connect(self._on_connect_callback)
        if self._on_disconnect_callback:
            self.messenger.set_on_disconnect(self._on_disconnect_callback)
        if self._on_sync_complete_callback:
            self.messenger.set_on_sync_complete(self._on_sync_complete_callback)

    async def login(self, username: str, password: str) -> bool:
        self.messenger = Messenger(username)
        self._current_username = username
        self._apply_callbacks()

        if await self.messenger.login(password):
            self._current_display_name = await self.messenger.ssn_mngr.db.identity.get_display_name()
            create_task(self._initial_sync())
            create_task(self.messenger.connect())
            return True
        
        self.messenger = None
        self._current_username = None
        return False
    
    async def register(self, username: str, display_name: str, password: str) -> bool:
        self.messenger = Messenger(username)
        self._current_username = username
        self._apply_callbacks()

        if await self.messenger.register(display_name, password):
            if await self.messenger.login(password):
                self._current_display_name = await self.messenger.ssn_mngr.db.identity.get_display_name()
                create_task(self._initial_sync())
                create_task(self.messenger.connect())
                return True
        
        self.messenger = None
        self._current_username = None
        return False
    
    async def _initial_sync(self):
        await self.messenger.load_offline_data()

    async def logout(self) -> None:
        if self.messenger:
            await self.messenger.close()
            self.messenger = None
            self._current_username = None
        
    async def update_display_name(self, display_name: str) -> bool:
        if self.messenger is None:
            return False
        success = await self.messenger.api.users.update_display_name(
            username = self.messenger.username,
            display_name = display_name
        )
        if success:
            await self.messenger.ssn_mngr.db.identity.save_display_name(
                display_name = display_name
            )
            return True
        return False
    
    async def get_display_name(self, username: str) -> str:
        if username in self._display_names_cache:
            return self._display_names_cache[username]
        if self.messenger is None:
            return username
        info = await self.messenger.api.users.display_info([username])
        if info and username in info:
            display_name = info[username].get("display_name", username)
        else:
            display_name = username
        self._display_names_cache[username] = display_name
        return display_name
    
    async def search_users(self, query: str) -> list[dict[str, Any]]:
        if not self.messenger:
            return []
        users = await self.messenger.api.users.search(query)
        if not users:
            return []
        return [{
            "username": user.get("username"),
            "display_name": user.get("display_name", ""),
        } for user in users if user.get("username") != self._current_username]
    
    async def get_chats(self) -> list[dict[str, Any]]:
        if self.messenger is None:
            return []
        chats = await self.messenger.get_chats()
        return chats

    async def get_chat_messages(self, interlocutor: str) -> list[dict[str, Any]]:
        if self.messenger is None:
            return []
        return await self.messenger.get_chat_messages(interlocutor)
    
    async def send_text_message(self, recipient: str, text: str) -> str | None:
        if self.messenger is None:
            return None
        result = await self.messenger.send_text_message(recipient, text)
        if result:
            return datetime.now(timezone.utc).isoformat()
        else:
            None
    
    def set_on_message(self, callback: Callable[[str, str, str], Any]) -> None:
        self._on_message_callback = callback
        if self.messenger:
            self.messenger.set_on_message(callback)

    def set_on_connect(self, callback: Callable[[], Any]) -> None:
        self._on_connect_callback = callback
        if self.messenger:
            self.messenger.set_on_connect(callback)

    def set_on_disconnect(self, callback: Callable[[int | None, str], Any]) -> None:
        self._on_disconnect_callback = callback
        if self.messenger:
            self.messenger.set_on_disconnect(callback)

    def set_on_sync_complete(self, callback: Callable[[], Any]) -> None:
        self._on_sync_complete_callback = callback
        if self.messenger:
            self.messenger.set_on_sync_complete(callback)

    @property
    def current_username(self) -> str | None:
        return self._current_username
    
    @property
    def current_display_name(self) -> str | None:
        return self._current_display_name
    
    @property
    def is_connected(self) -> bool:
        if self.messenger is None:
            return False
        return self.messenger.is_connected
