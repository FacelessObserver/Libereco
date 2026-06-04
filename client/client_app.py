import flet as ft
from typing import Optional
from app.controller import AppController
from ui.auth_view.auth_view import AuthView
from ui.main_view.main_view import MainView

class MessengerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = AppController()
        self.current_view: Optional[ft.Control] = None
        self.main_view: Optional[MainView] = None

        self._setup_page()
        self._show_auth_view()

    def _setup_page(self):
        self.page.title = "Libereco Messenger"
        self.page.bgcolor = ft.Colors.BLACK
        self.page.window.width = 1280
        self.page.window.height = 720
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.CrossAxisAlignment.CENTER

    def _show_auth_view(self):
        auth_view = AuthView(
            on_login = self._handle_login,
            on_register = self._handle_register
        )
        self.current_view = auth_view
        self.page.clean()
        self.page.add(auth_view)
        self.page.update()

    async def _show_main_view(self):
        username = self.controller.current_username
        display_name = self.controller.current_display_name
        if not username:
            return
        
        if self.main_view:
            if self.main_view in self.page.controls:
                self.page.controls.remove(self.main_view)
            self.main_view = None
            self.controller.set_on_message(None)

        self.main_view = MainView(
            username = username,
            display_name = display_name or username,
            on_profile_click = self._handle_profile_click,
            on_search = self._handle_search,
            on_search_empty = self._handle_search_empty,
            on_search_focus = self._handle_search_focus,
            on_chat_selected = self._handle_chat_selected,
            on_send_message = self._handle_send_message,
            on_load_messages = self._handle_load_messages,
            on_logout = self._handle_logout,
            on_edit_display_name = self._handle_edit_display_name
        )
        self.current_view = self.main_view
        self.page.clean()
        self.page.add(self.main_view)
        self.page.update()

        self.controller.set_on_message(self._on_new_message)
        self.controller.set_on_sync_complete(self._on_sync_complete)

    async def _handle_login(self, username: str, password: str) -> bool:
        success = await self.controller.login(username, password)
        if success:
            await self._show_main_view()
        return success

    async def _handle_register(self, username: str, display_name: str, password: str) -> bool:
        success = await self.controller.register(username, display_name, password)
        print(username, display_name, password, success)
        if success:
            await self._show_main_view()
        return success
    
    async def _refresh_chats(self):
        if not self.main_view:
            return
        chats = await self.controller.get_chats()
        self.main_view.update_chats(chats)

    async def _handle_chat_selected(self, username: str, display_name: str):
        print(f"Selected chat: {username}, {display_name}")

    async def _handle_load_messages(self, interlocutor: str) -> list[dict]:
        messages = await self.controller.get_chat_messages(interlocutor)
        return messages

    async def _handle_send_message(self, recipient: str, text: str) -> str | None:
        time = await self.controller.send_text_message(recipient, text)
        if time and self.main_view:
            display_name = recipient
            if self.main_view.chat_view and self.main_view.chat_view.display_name:
                display_name = self.main_view.chat_view.display_name
            self.main_view.update_chat_last_message(
                username = recipient,
                is_from_me = True,
                last_message = text,
                time = time,
                display_name = display_name
            )
            return time
        else:
            return None

    async def _on_sync_complete(self):
        await self._refresh_chats()

    async def _on_new_message(self, from_username: str, message: str, timestamp: str):
        if self.main_view:
            display_name = await self.controller.get_display_name(from_username)
            await self.main_view.add_message(
                username = from_username,
                message = message,
                is_from_me = False,
                time = timestamp
            )

            self.main_view.update_chat_last_message(
                username = from_username,
                is_from_me = False,
                last_message = message,
                time = timestamp,
                display_name = display_name
            )

    async def _handle_search(self, query: str) -> list[dict]:
        results = await self.controller.search_users(query)
        return results

    async def _handle_search_empty(self):
        print("Empty search") # Сделаю в будущем

    async def _handle_search_focus(self):
        print("Focus") # Сделаю в будущем
    
    async def _handle_edit_display_name(self, new_display_name: str):
        success = await self.controller.update_display_name(new_display_name)
        if success:
            if self.main_view:
                self.main_view.update_display_name(new_display_name)
        else:
            print("Failed to update display name") # Сделаю в будущем

    async def _handle_profile_click(self):
        print("Profile click") # Сделаю в будущем
    
    async def _handle_logout(self):
        self.controller.set_on_message(None)
        self.controller.set_on_sync_complete(None)
        await self.controller.logout()
        if self.main_view:
            self.main_view = None
        self._show_auth_view()

def main(page: ft.Page):
    MessengerApp(page)

if __name__ == "__main__":
    ft.run(main = main)
