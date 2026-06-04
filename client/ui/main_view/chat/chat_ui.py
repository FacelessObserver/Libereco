import flet as ft
from typing import Callable
from ...sources.styles import Colors, Sizes

class ChatUI(ft.Container):
    def __init__(
        self,
        close_button_on_click: Callable,
        message_field_on_submit: Callable,
        send_button_on_click: Callable,
        logo_path: str = "client/ui/sources/Libereco_logo.svg"
    ):
        super().__init__()

        self.title = ft.Text(
            color = Colors.TEXT_PRIMARY,
            size = 20,
            weight = ft.FontWeight.BOLD
        )

        self.close_button = ft.IconButton(
            icon = ft.Icons.CLOSE,
            icon_color = Colors.PRIMARY,
            icon_size = 25,
            on_click = close_button_on_click
        )

        self.messages_list = ft.ListView(
            auto_scroll = False,
            expand = True,
            padding = ft.Padding.all(
                Sizes.PADDING_MEDIUM
            ),
            spacing = 10
        )

        self.message_field = ft.TextField(
            hint_text = "Enter message",
            multiline = True,
            min_lines = 1,
            max_lines = 3,
            shift_enter = True,
            expand = True,
            border_radius = 16,
            border_color = Colors.BACKGROUND_LIGHT,
            bgcolor = Colors.BACKGROUND_LIGHT,
            color = Colors.TEXT_PRIMARY,
            cursor_color = Colors.PRIMARY,
            on_submit = message_field_on_submit
        )

        self.send_button = ft.IconButton(
            icon = ft.Icons.SEND_ROUNDED,
            icon_color = Colors.PRIMARY,
            icon_size = 25,
            on_click = send_button_on_click
        )

        self.empty_state = ft.Container(
            expand = True,
            alignment = ft.Alignment.CENTER,
            content = ft.Column(
                controls = [
                    ft.Image(
                        src = logo_path,
                    ),
                    ft.Text(
                        value = "Select chat",
                        size = 24,
                        color = Colors.TEXT_SECONDARY
                    )
                ],
                alignment = ft.CrossAxisAlignment.CENTER,
                horizontal_alignment = ft.CrossAxisAlignment.CENTER
            )
        )

        self.chat_content = ft.Column(
            visible = False,
            expand = True,
            spacing = 0,
            controls = [
                ft.Container(
                    padding = ft.Padding.symmetric(
                        horizontal = 20,
                        vertical = 5
                    ),
                    height = 70,
                    border = ft.Border.only(
                        bottom = ft.BorderSide(
                            color = Colors.BACKGROUND_LIGHT,
                            width = 1
                        )
                    ),
                    content = ft.Row(
                        controls = [
                            self.title,
                            self.close_button,
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment = ft.CrossAxisAlignment.CENTER,
                    )
                ),
                self.messages_list,
                ft.Container(
                    border = ft.Border.only(
                        top = ft.BorderSide(
                            color = Colors.BACKGROUND_LIGHT,
                            width = 1
                        )
                    ),
                    content = ft.Row(
                        controls = [
                            self.message_field,
                            self.send_button
                        ],
                        vertical_alignment = ft.CrossAxisAlignment.END
                    ),
                    padding = 15
                )
            ]
        )

        self.expand = True
        self.bgcolor = Colors.BACKGROUND
        self.content = ft.Stack(
            controls = [
                self.chat_content,
                self.empty_state
            ],
            expand = True
        )
