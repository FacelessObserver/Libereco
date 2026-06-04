import flet as ft
from ....sources.styles import Colors, Sizes

class Profile(ft.Container):
    def __init__(
        self,
        username: str,
        display_name: str,
        on_logout,
        on_edit_display_name,
        on_close
    ):
        super().__init__()

        self.username = username
        self.display_name = display_name
        self.on_logout = on_logout
        self.on_edit_display_name = on_edit_display_name
        self.on_close = on_close

        self._edit_mode = False

        self.avatar = ft.CircleAvatar(
            content = ft.Text(
                value = (self.display_name[:1] or "?").upper(),
                size = 60,
                color = Colors.PRIMARY
            ),
            bgcolor = Colors.BACKGROUND_LIGHT,
            radius = 60
        )
    
        self.username_text = ft.Text(
            value = f"@{self.username}",
            size = 24,
            weight = ft.FontWeight.BOLD,
            color = Colors.PRIMARY
        )

        self.avatar_username_column = ft.Column(
            controls = [
                self.avatar,
                self.username_text
            ],
            spacing = 10,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER
        )
    
        self.display_name_text = ft.Text(
            value = self.display_name,
            size = 24,
            weight = ft.FontWeight.BOLD,
            color = Colors.PRIMARY,
            overflow = ft.TextOverflow.ELLIPSIS,
            expand = True 
        )

        self.display_name_field = ft.TextField(
            value = self.display_name,
            disabled = True,
            dense = True,
            border = ft.InputBorder.UNDERLINE,
            text_size = 24,
            color = Colors.PRIMARY,
            bgcolor = Colors.BACKGROUND,
            expand = True,
            visible =  False
        )

        self.display_name_edit_button = ft.IconButton(
            icon = ft.Icons.EDIT,
            icon_color = Colors.PRIMARY,
            on_click = self._toggle_edit
        )

        self.display_name_row = ft.Row(
            controls = [
                self.display_name_text,
                self.display_name_field,
                self.display_name_edit_button
            ],
            spacing = 6,
            alignment = ft.MainAxisAlignment.START
        )
    
        self.logout_button = ft.Button(
            content = ft.Text(
                value = "Logout"
            ),
            style = ft.ButtonStyle(
                color = Colors.PRIMARY
            ),
            icon = ft.Icons.EXIT_TO_APP,
            icon_color = Colors.ERROR,
            on_click = self._handle_logout
        )

        self.close_button = ft.IconButton(
            icon = ft.Icons.ARROW_BACK,
            icon_color = Colors.PRIMARY,
            on_click = self._close_click,
            tooltip = "Back to chats",
            icon_size = 25
        )

        self.header_row = ft.Row(
            controls = [
                self.close_button,
                ft.Text(
                    value = "Profile",
                    size = 25,
                    weight = ft.FontWeight.BOLD,
                    color = Colors.TEXT_PRIMARY
                )
            ],
            alignment = ft.MainAxisAlignment.START,
            vertical_alignment = ft.CrossAxisAlignment.CENTER
        )

        self.header_container = ft.Container(
            content = self.header_row,
            padding = ft.Padding.symmetric(
                horizontal = 2 * Sizes.PADDING_MEDIUM,
                vertical = 5
            ),
            height = 70,
            border = ft.Border.only(
                bottom = ft.BorderSide(
                    color = Colors.BACKGROUND_LIGHT,
                    width = 1
                )
            )
        )
    
        self.content = ft.Column(
            controls = [
                self.header_container,
                ft.Column(
                    margin = ft.Margin.symmetric(
                        horizontal = 100
                    ),
                    controls=[
                        self.avatar_username_column,
                        ft.Divider(height = 20),
                        self.display_name_row,
                        ft.Divider(height = 20),
                        self.logout_button
                    ],
                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                    spacing = 10,
                    expand = True,
                    alignment = ft.MainAxisAlignment.CENTER
                )
            ],
            spacing = 0,
            expand = True
        )
    
    async def _handle_logout(self, e):
        if self.on_logout:
            await self.on_logout()
    
    def _set_edit_mode(self, enabled: bool):
        self._edit_mode = enabled

        self.display_name_text.visible = not enabled
        self.display_name_field.visible = enabled
        self.display_name_field.disabled = not enabled

        self.display_name_edit_button.icon = (
            ft.Icons.SAVE if enabled else ft.Icons.EDIT
        )

        self.display_name_edit_button.icon_color = (
            Colors.SUCCESS if enabled else Colors.PRIMARY
        )
  
    async def _toggle_edit(self, e):
        if not self._edit_mode:
            self._original_display_name = self.display_name
            self.display_name_field.value = self.display_name

            self._set_edit_mode(True)
            self.update()
            
            await self.display_name_field.focus()
            return
        
        new_display_name = self.display_name_field.value.strip() or self.username

        try:
            if new_display_name != self._original_display_name and self.on_edit_display_name:
                await self.on_edit_display_name(new_display_name)
            
            self.display_name = new_display_name
            self.display_name_text.value = new_display_name
            if self.avatar.content and isinstance(self.avatar.content, ft.Text):
                self.avatar.content.value = (new_display_name[:1] or "?").upper()
                self.avatar.content.update()
            else:
                self.avatar.content = ft.Text(
                    value = (new_display_name[:1] or "?").upper(),
                    size = 60,
                    color = Colors.PRIMARY
                )
        finally:
            self._set_edit_mode(False)
            self.update()
    
    def _close_click(self, e):
        if self.on_close:
            self.on_close()
