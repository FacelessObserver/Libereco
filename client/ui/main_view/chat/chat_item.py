import flet as ft
from datetime import datetime
from ...sources.styles import Colors, Sizes

class ChatItem(ft.Container):
    
    def __init__(self, message: str, is_from_me: bool, time: str):
        super().__init__(
            content = ft.Column(
                controls = [
                    ft.Text(
                        value = message,
                        size = Sizes.FONT_MEDIUM,
                        color = Colors.TEXT_PRIMARY,
                        selectable = True,
                        no_wrap = False
                    ),
                    ft.Text(
                        value = self._format_time(time),
                        size = 10,
                        color = Colors.TEXT_SECONDARY,
                    )
                ],
                spacing = 4,
                tight = True,
                horizontal_alignment = (
                    ft.CrossAxisAlignment.END
                    if is_from_me else
                    ft.CrossAxisAlignment.START
                )
            ),

            bgcolor = (
                Colors.BACKGROUND_SUP_LIGHT
                if is_from_me else
                Colors.BACKGROUND_LIGHT
            ),

            margin = ft.margin.symmetric(
                horizontal = 8
            ),

            padding = ft.Padding.all(Sizes.PADDING_MEDIUM),
            border_radius = Sizes.BORDER_RADIUS_LARGE
        )

    def _format_time(self, time: str) -> str:
        try:
            dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
            return dt.strftime("%d.%m %H:%M")
        except Exception:
            return time
