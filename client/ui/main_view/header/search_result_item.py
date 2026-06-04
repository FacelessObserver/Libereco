import flet as ft
from ...sources.styles import Colors, Sizes

class SearchResultItem(ft.Container):
    def __init__(self, username: str, display_name: str, on_click_cb):
        super().__init__()
        self.username = username
        self.display_name = display_name
        self._on_click_cb = on_click_cb

        self._normal_bg = Colors.BACKGROUND_LIGHT
        self._hover_bg = Colors.BACKGROUND

        self.avatar = ft.CircleAvatar(
            content = ft.Text(
                value = (display_name[:1] or "?").upper(),
                size = 20,
                color = Colors.BACKGROUND,
                weight = ft.FontWeight.BOLD
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
            value = f"@{username}",
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

        self.content = ft.Row(
            controls = [
                self.avatar,
                ft.Column(
                    controls = [
                        ft.Row(
                            controls = [
                                self.title
                            ],
                            alignment = ft.MainAxisAlignment.START
                        )
                    ],
                    expand = True,
                    spacing = 5
                )
            ],
            spacing = 12,
            vertical_alignment = ft.CrossAxisAlignment.CENTER
        )
        
        self.padding = Sizes.PADDING_MEDIUM
        self.border_radius = Sizes.BORDER_RADIUS_MEDIUM
        self.bgcolor = self._normal_bg

        self.on_click = self._on_click
        self.on_hover = self._on_hover

    async def _on_click(self, e):
        if self._on_click_cb:
            await self._on_click_cb(self.username, self.display_name)

    def _on_hover(self, e):
        self.bgcolor = self._hover_bg if e.data == "true" else self._normal_bg
        self.update()
