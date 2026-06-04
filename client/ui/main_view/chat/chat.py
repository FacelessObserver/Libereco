import flet as ft
from typing import Awaitable, Callable
from .chat_item import ChatItem
from .chat_ui import ChatUI

class Chat(ChatUI):
    def __init__(
        self,
        on_send_message: Callable[[str, str], Awaitable[str]],
        load_callback = [Callable[[str], Awaitable[list[dict]]]]
    ):
        super().__init__(
            close_button_on_click = self._clear_chat,
            message_field_on_submit = self._on_submit,
            send_button_on_click = self._on_submit,
        )
        self.username = None
        self.display_name = None
        self.on_send_message = on_send_message
        self.load_callback = load_callback

        self.drafts: dict[str, str] = {} 
        self.messages_cache: dict[str, list[dict]] = {}

    async def set_chat(
        self,
        username: str,
        display_name: str,
    ) -> None:
        self._save_draft()
        self.username = username
        self.display_name = display_name

        self.title.value = f"{display_name} @{username}"
        self.message_field.value = self.drafts.get(username, "")

        self.empty_state.visible = False
        self.chat_content.visible = True
        self.messages_list.controls.clear()
        self.update()

        if username in self.messages_cache and self.messages_cache[username]:
            await self._display_messages(self.messages_cache[username])
        else:
            await self._load_messages(username)
            if self.username == username:
                await self._display_messages(self.messages_cache[username])

    async def add_message(
        self,
        username: str,
        message: str,
        is_from_me: bool,
        time: str
    ) -> None:
        if username not in self.messages_cache :
            self.messages_cache[username] = []
            await self._load_messages(username)
            return

        self.messages_cache[username].append({
            "message": message,
            "is_from_me": is_from_me,
            "time": time
        })

        if self.username == username:
            container = self._create_message_container(
                message = message,
                is_from_me = is_from_me,
                time = time
            )
            self.messages_list.controls.append(container)
            self.messages_list.update()
            await self._scroll_to_bottom(300)
    
    def _clear_chat(self) -> None:
        self.chat_content.visible = False
        self.empty_state.visible = True
        self._save_draft()
        self.username = None
        self.display_name = None
        self.messages_list.controls.clear()
        self.message_field.value = ""
        self.update()

    def _save_draft(self) -> None:
        if self.username:
            draft_text = self.message_field.value.strip()
            if draft_text:
                self.drafts[self.username] = draft_text
            elif self.username in self.drafts:
                self.drafts.pop(self.username, None)
    
    async def _scroll_to_bottom(self, duration: int = 0):
        await self.messages_list.scroll_to(offset = -1.0, duration = duration)

    async def _display_messages(self, messages: list[dict]) -> None:
        self.messages_list.controls.clear()
        for message in messages:
            container = self._create_message_container(
                message.get("message"),
                message.get("is_from_me"),
                message.get("time")
            )
            self.messages_list.controls.append(container)
        self.messages_list.update()
        if self.messages_list.controls:
            await self._scroll_to_bottom()
    
    async def _load_messages(
        self,
        username: str,
    ) -> None:
        try:
            messages = await self.load_callback(username)
            if username not in self.messages_cache or not self.messages_cache[username]:
                self.messages_cache[username] = messages.copy()
        except Exception as e:
            if self.username == username:
                self.page.show_dialog(
                    ft.SnackBar(
                        content = ft.Text(
                            value = f"Load messages error: {e}"
                        )
                    )
                )

    def _create_message_container(
        self,
        message: str,
        is_from_me: bool,
        time: str
    ) -> ft.Container:
        return ft.Container(
            content = ChatItem(
            message = message,
            is_from_me = is_from_me,
            time = time
            ),
            alignment = (
                ft.Alignment.CENTER_RIGHT
                if is_from_me else
                ft.Alignment.CENTER_LEFT
            ),
            expand = False,
        )

    async def _on_submit(self, e) -> None:
        message = self.message_field.value.strip()
        if not message or not self.username:
            return

        time = await self.on_send_message(self.username, message)
        if time:
            self.drafts.pop(self.username, None)
            self.message_field.value = ""
            self.message_field.update()

            await self.add_message(
                username = self.username,
                message = message,
                is_from_me = True,
                time = time
            )
        else:
            self.page.show_dialog(
                ft.SnackBar(
                    bgcolor = ft.Colors.WHITE,
                    content = ft.Text(
                        color = ft.Colors.BLACK,
                        value = f"Send message error"
                    ),
                    duration = 3000
                )
            )
