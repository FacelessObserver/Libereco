import flet as ft
from .chats_list_item import ChatListItem
from ...sources.styles import Colors, Sizes

class ChatsList(ft.Container):
    def __init__(self, on_chat_selected):
        super().__init__()

        self.on_chat_selected = on_chat_selected

        self.chats_cache: dict[str, ChatListItem] = {}

        self.chats_list = ft.ListView(
            spacing = 8,
            padding = ft.padding.all(Sizes.PADDING_MEDIUM),
            expand = True
        )

        self.empty_text = ft.Text(
            value = "No chats",
            size = Sizes.FONT_MEDIUM,
            color = Colors.TEXT_SECONDARY
        )

        self.empty_state = ft.Container(
            alignment = ft.Alignment.CENTER,
            content = self.empty_text,
            expand = True,
            visible = True
        )

        self.list_layer = ft.Container(
            content = self.chats_list,
            expand = True,
            visible = False
        )

        self.content = ft.Stack(
            controls = [
                self.list_layer,
                self.empty_state
            ],
            expand = True
        )

        self.bgcolor = Colors.BACKGROUND
        self.expand = True

    def load_chats(self, chats: list[dict]) -> None:
        self.chats_list.controls.clear()
        self.chats_cache.clear()

        for chat in chats:
            username = chat.get("username") or chat.get("interlocutor")

            item = ChatListItem(
                username = username,
                display_name = chat.get("display_name"),
                is_from_me = chat.get("is_from_me"),
                last_message = chat.get("last_message"),
                time = chat.get("time"),
                on_click = self.on_chat_selected
            )

            self.chats_cache[username] = item
            self.chats_list.controls.append(item)
        
        self.chats_list.controls.sort(
            key = lambda x: x.time or "",
            reverse = True
        )
        self._update_visibility()
    
    def update_chat(
        self,
        username: str,
        is_from_me: bool,
        last_message: str,
        time: str 
    ) -> None:
        item = self.chats_cache.get(username)
        if not item:
            return
        
        item.update_data(is_from_me, last_message, time)

        if self.chats_list.controls[0] != item:
            self.chats_list.controls.remove(item)
            self.chats_list.controls.insert(0, item)
        
        self.update()

    def add_chat(
        self,
        username: str,
        display_name: str,
        is_from_me: bool,
        last_message: str,
        time: str
    ) -> None:
        if username in self.chats_cache:
            return
        
        item = ChatListItem(
            username = username,
            display_name = display_name,
            is_from_me = is_from_me,
            last_message = last_message,
            time = time,
            on_click = self.on_chat_selected,
        )

        self.chats_cache[username] = item
        self.chats_list.controls.insert(0, item)
        self._update_visibility()
    
    def _update_visibility(self) -> None:
        has_chats = len(self.chats_list.controls) > 0
        self.empty_state.visible = not has_chats
        self.list_layer.visible = has_chats
        self.update()
