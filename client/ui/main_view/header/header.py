import flet as ft
from .search_field import SearchField
from ...sources.styles import Colors, Sizes

class HeaderView(ft.Container):
    def __init__(
        self,
        display_name: str,
        on_profile_click = None,
        on_search = None,
        on_search_empty = None,
        on_search_focus = None,
    ):
        super().__init__()
        self.on_search_focus_callback = on_search_focus

        self.height = 70

        self.padding = ft.Padding.only(
            left = 2 * Sizes.PADDING_MEDIUM,
            right = Sizes.PADDING_MEDIUM,
            top = Sizes.PADDING_SMALL,
            bottom = Sizes.PADDING_SMALL
        )

        self.bgcolor = Colors.BACKGROUND

        self.avatar = ft.CircleAvatar(
            content = ft.Text(
                value = (display_name[:1] or "?").upper(),
                color = Colors.PRIMARY,
                size = 20,
                weight = ft.FontWeight.BOLD
            ),
            radius = 25,
            bgcolor = Colors.BACKGROUND_LIGHT
        )

        self.profile_button = ft.Container(
            content = self.avatar,
            on_click = on_profile_click,
            tooltip = "Profile"
        )


        self.search_field = SearchField(
            on_search = on_search,
            on_empty = on_search_empty,
            on_focus = on_search_focus,
        )
        
        self.content = ft.Row(
            controls = [
                self.profile_button,
                ft.Container(
                    expand = True,
                    margin = ft.margin.only(
                        left = Sizes.PADDING_MEDIUM
                    ),
                    content = self.search_field
                )
            ],
            alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment = ft.CrossAxisAlignment.CENTER
        )
    
    def update_display_name(self, new_display_name: str):
        self.display_name = new_display_name
        if self.avatar.content and isinstance(self.avatar.content, ft.Text):
            self.avatar.content.value = (new_display_name[:1] or "?").upper()
            self.avatar.content.update()
            self.update()
    
    async def _on_focus(self, e):
        if self.on_search_focus_callback:
            await self.on_search_focus_callback()
