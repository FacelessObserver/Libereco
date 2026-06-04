import flet as ft
from datetime import datetime
from typing import Callable, Awaitable, Optional
from .chat.chat import Chat
from .chats.chats_list import ChatsList
from .header.header import HeaderView
from .header.search_result_item import SearchResultItem
from .header.profile.profile import Profile
from ..sources.styles import Colors, Sizes

class MainView(ft.Container):
    def __init__(
        self,
        username: str,
        display_name: str,
        on_profile_click: Optional[Callable[[], None]] = None,
        on_search: Optional[Callable[[str], Awaitable[list[dict]]]] = None,
        on_search_empty: Optional[Callable[[], None]] = None,
        on_search_focus: Optional[Callable[[], None]] = None,
        on_chat_selected: Optional[Callable[[str, str], Awaitable[None]]] = None,
        on_send_message: Optional[Callable[[str, str], Awaitable[str]]] = None,
        on_load_messages: Optional[Callable[[str], Awaitable[list[dict]]]] = None,
        on_logout: Optional[Callable[[], None]] = None,
        on_edit_display_name: Optional[Callable[[str], Awaitable[None]]] = None
    ):
        super().__init__()
        self.username = username
        self.display_name = display_name

        self.on_profile_click = on_profile_click
        self.on_search = on_search
        self.on_search_empty = on_search_empty
        self.on_search_focus = on_search_focus
        self.on_chat_selected = on_chat_selected
        self.on_send_message = on_send_message
        self.on_load_messages = on_load_messages
        self.on_logout = on_logout
        self.on_edit_display_name = on_edit_display_name

        self.chat_view = Chat(
            on_send_message = self._handle_send_message,
            load_callback = on_load_messages
        )

        self.chats_view = ChatsList(
            on_chat_selected = self._handle_chat_selected
        )

        self.header_view = HeaderView(
            display_name = self.display_name,
            on_profile_click = self._open_profile,
            on_search = self._handle_search,
            on_search_empty = self._handle_search_empty,
            on_search_focus=self._show_search_panel
        )

        self.chats_container = ft.Container(
            content = self.chats_view,
            expand = True,
            visible = True
        )

        self.search_results_list = ft.ListView(
            spacing = 8,
            padding = ft.padding.all(Sizes.PADDING_MEDIUM),
            expand = True
        )
        self.search_container = ft.Container(
            content = self.search_results_list,
            expand = True,
            visible = False
        )

        self.content_stack = ft.Stack(
            controls = [
                self.chats_container,
                self.search_container
            ],
            expand = True
        )

        self.normal_panel = ft.Container(
            content = ft.Column(
                spacing = 0,
                controls = [
                    self.header_view,
                    self.content_stack
                ],
                expand = True
            ),
            expand = True,
            visible = True,
            border = ft.Border.only(
                right = ft.BorderSide(
                    color = Colors.BACKGROUND_LIGHT,
                    width = 1
                )
            )
        )

        self.profile_container = ft.Container(
            content = Profile(
                username = self.username,
                display_name = self.display_name,
                on_logout = self.on_logout,
                on_edit_display_name = self.on_edit_display_name,
                on_close = self._close_profile
            ),
            expand = True,
            visible = False,
            border = ft.Border.only(
                right = ft.BorderSide(
                    color = Colors.BACKGROUND_LIGHT,
                    width = 1
                )
            )
        )

        self.left_panel = ft.Stack(
            controls = [
                self.normal_panel,
                self.profile_container
            ],
            expand = True
        )

        self.right_panel = ft.Container(
            expand = True,
            content = self.chat_view,
            bgcolor = Colors.BACKGROUND
        )

        self.content = ft.Row(
            spacing = 0,
            expand = True,
            controls = [
                ft.Container(expand = 4, content = self.left_panel),
                ft.Container(expand = 6, content = self.right_panel),
            ]
        )

        self.expand = True
        self.bgcolor = Colors.BACKGROUND
        
    def _open_profile(self):
        self.normal_panel.visible = False
        self.profile_container.visible = True
        self.update()

    def _close_profile(self):
        self.profile_container.visible = False
        self.normal_panel.visible = True
        self.update()

    async def _show_search_panel(self):
        self.normal_panel.visible = True
        self.profile_container.visible = False
        self.chats_container.visible = False
        self.search_container.visible = True
        self.update()

    async def _hide_search_panel(self):
        self.search_container.visible = False
        self.chats_container.visible = True
        self.search_results_list.controls.clear()
        self.search_results_list.update()
        self.update()

    async def _handle_search(self, query: str):
        if not query.strip():
            await self._handle_search_empty()
            return
        if self.on_search:
            users = await self.on_search(query)
            self._display_search_results(users)

    async def _handle_search_empty(self):
        self.search_results_list.controls.clear()
        self.search_results_list.update()
        await self._hide_search_panel()
        if self.on_search_empty:
            await self.on_search_empty()

    def _display_search_results(self, users: list[dict]):
        self.search_results_list.controls.clear()
        for user in users:
            username = user.get("username")
            display_name = user.get("display_name") or username
            item = SearchResultItem(
                username = username,
                display_name = display_name,
                on_click_cb = self._on_search_result_click,
            )
            self.search_results_list.controls.append(item)
        self.search_results_list.update()
        if not self.search_container.visible:
            self.search_container.visible = True
            self.chats_container.visible = False
            self.update()

    def _on_result_hover(self, is_hovered: bool):
        self._search_result_hovered = is_hovered

    async def _on_search_result_click(self, username: str, display_name: str):
        try:
            self.header_view.search_field.value = ""
            self.header_view.search_field.update()
            self.search_results_list.controls.clear()
            self.search_results_list.update()
            self.search_container.visible = False
            self.chats_container.visible = True
            self.update()
            await self._handle_chat_selected(username, display_name)
        finally:
            self._search_result_hovered = False 

    async def _handle_chat_selected(self, username: str, display_name: str):
        await self.chat_view.set_chat(username, display_name)
        if self.on_chat_selected:
            await self.on_chat_selected(username, display_name)

    async def _handle_send_message(self, username: str, message: str) -> str:
        if self.on_send_message:
            return await self.on_send_message(username, message)
        return datetime.now().isoformat()

    def update_chats(self, chats: list[dict]):
        if self.chats_view:
            self.chats_view.load_chats(chats)

    def add_chat(self, username: str, display_name: str):
        if self.chats_view:
            self.chats_view.add_chat(username, display_name)

    async def add_message(self, username: str, message: str, is_from_me: bool, time: str):
        await self.chat_view.add_message(
            username = username,
            message = message,
            is_from_me = is_from_me,
            time = time
        )

    def update_display_name(self, new_display_name: str):
        self.display_name = new_display_name
        self.header_view.update_display_name(new_display_name)
        if self.profile_container.visible:
            profile = self.profile_container.content
            profile.display_name = new_display_name
            profile.display_name_text.value = new_display_name
            if profile.avatar.content and isinstance(profile.avatar.content, ft.Text):
                profile.avatar.content.value = (new_display_name[:1] or "?").upper()
                profile.avatar.content.update()
            profile.update()

    def update_chat_last_message(
        self,
        username: str,
        is_from_me: bool,
        last_message: str,
        time: str,
        display_name: str
    ):
        if not self.chats_view:
            return
        display_name = display_name or username
        if username not in self.chats_view.chats_cache:
            self.chats_view.add_chat(username, display_name, is_from_me, last_message, time)
        else:
            self.chats_view.update_chat(username, is_from_me, last_message, time)
