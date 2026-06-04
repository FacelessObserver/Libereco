import flet as ft
from datetime import datetime
from typing import Awaitable, Callable, Optional
from ...sources.styles import Colors, Sizes

class ChatListItem(ft.Container):
    def __init__(
            self,
            username: str,
            display_name: str,
            is_from_me: Optional[bool],
            last_message: Optional[str],
            time: Optional[str],
            on_click: Callable[[], Awaitable[None]]
    ):
        super().__init__()

        self.username = username
        self.display_name = display_name
        self.is_from_me = is_from_me
        self.last_message = last_message
        self.time = time
        self._on_click_cb = on_click

        self._normal_bg = Colors.BACKGROUND_LIGHT
        self._hover_bg = Colors.BACKGROUND

        self.avatar = ft.CircleAvatar(
            content = ft.Text(
                value = (display_name[:1] or "?").upper(),
                size = 20,
                color = Colors.BACKGROUND,
                weight = ft.FontWeight.BOLD,
            ),
            radius = 25,
            bgcolor = Colors.PRIMARY
        )

        self.display_name_title = ft.Text(
            value = display_name,
            size = Sizes.FONT_LARGE,
            weight = ft.FontWeight.BOLD,
            color = Colors.TEXT_PRIMARY,
            overflow = ft.TextOverflow.ELLIPSIS
        )

        self.username_title = ft.Text(
            value = f"@{self.username}",
            size = Sizes.FONT_SMALL,
            weight = ft.FontWeight.NORMAL,
            color = Colors.TEXT_SECONDARY,
            overflow = ft.TextOverflow.ELLIPSIS
        )

        self.title = ft.Row(
            controls = [
                self.display_name_title,
                self.username_title
            ],
            spacing = 6,
            alignment = ft.MainAxisAlignment.START,
            expand = True
        )

        self.time_text = ft.Text(
            self._format_time(time) if time else "",
            size = Sizes.FONT_SMALL,
            color = Colors.TEXT_SECONDARY
        )

        self.message_text = ft.Text(
            value = self.build_message_text(
                is_from_me,
                last_message
            ),
            size = Sizes.FONT_MEDIUM,
            color = Colors.TEXT_SECONDARY,
            max_lines = 1,
            overflow = ft.TextOverflow.ELLIPSIS,
            expand = True
        )

        self.content = ft.Row(
            controls = [
                self.avatar,
                ft.Column(
                    controls = [
                        ft.Row(
                            controls = [self.title, self.time_text],
                            alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(controls = [self.message_text])
                    ],
                    expand = True,
                    spacing = 5
                ),
            ],
            spacing = 12,
            vertical_alignment = ft.CrossAxisAlignment.CENTER
        )

        self.padding = Sizes.PADDING_MEDIUM
        self.border_radius = Sizes.BORDER_RADIUS_MEDIUM
        self.bgcolor = self._normal_bg
        self.on_click = self._on_click
        self.on_hover = self._on_hover

    def _format_time(self, time: str) -> str:
        try:
            dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
            return dt.strftime("%d.%m.%Y")
        except Exception:
            return time
    
    def update_data(self, is_from_me: bool, last_message: str, time: str) -> None:
        self.is_from_me = is_from_me
        self.last_message = last_message
        self.time = time

        self.message_text.value = self.build_message_text(
            is_from_me,
            last_message
        )
        self.time_text.value = self._format_time(time)

        self.update()
    
    def build_message_text(
        self,
        is_from_me: Optional[bool],
        last_message: Optional[str]
    ) -> str:
        prefix = "You: " if is_from_me else ""
        content = last_message or "No messages"

        return prefix + content

    async def _on_click(self, e) -> None:
        await self._on_click_cb(self.username, self.display_name)

    def _on_hover(self, e) -> None:
        self.bgcolor = self._hover_bg if e.data == "true" else self._normal_bg
        self.update()
