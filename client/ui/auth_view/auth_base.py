import flet as ft
from re import fullmatch
from ..sources.styles import(
    Colors,
    Sizes,
    INPUT_STYLE,
    ENABLED_BUTTON_STYLE,
    DISABLED_BUTTON_STYLE
) 

class AuthBase(ft.Container):
    def __init__(self):
        super().__init__()

        self.logo = ft.Image(
            src = "client/ui/sources/Libereco_logo.svg",
        )

        self.error_text = ft.Text(
            visible = False,
            selectable = False,
            color = Colors.ERROR,
            size = Sizes.FONT_SMALL,
        )

    def build_content(self, controls: list[ft.Control]) -> None:
        self.content = ft.Column(
            controls = [
                ft.Container(
                    content = self.logo,
                    margin = ft.Margin.only(
                        bottom = Sizes.PADDING_LARGE
                    )
                ),
                *controls,
                ft.Container(
                    content = self.error_text,
                    margin = ft.Margin.only(
                        top = Sizes.PADDING_SMALL
                    )
                )
            ],
            horizontal_alignment = ft.CrossAxisAlignment.CENTER
        )

    def create_text_field(self, label: str, password: bool = False) -> ft.TextField:
        return ft.TextField(
            label = label,
            password = password,
            can_reveal_password = password,
            autocorrect = False,
            width = 300,
            on_change = self._on_field_change,
            error_max_lines = 2,
            animate_size = ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            **INPUT_STYLE
        )

    def create_submit_button(self, text: str, on_click) -> ft.FilledButton:
        return ft.FilledButton(
            content = ft.Text(
                value = text
            ),
            disabled = True,
            style = DISABLED_BUTTON_STYLE,
            width = 300,
            height = 45,
            on_click = on_click
        )

    def create_switch_button(self, text: str, on_click) -> ft.TextButton:
        return ft.TextButton(
            content = ft.Text(
                value = text
            ),
            style = ft.ButtonStyle(
                color = Colors.PRIMARY,
                bgcolor = Colors.BACKGROUND
            ),
            width = 300,
            height = 45,
            on_click = on_click,
        )

    def set_button_enabled(self, button: ft.FilledButton, enabled: bool) -> None:
        button.disabled = not enabled
        button.style = (
            ENABLED_BUTTON_STYLE
            if enabled
            else DISABLED_BUTTON_STYLE
        )
        button.update()

    def show_error(self, message: str) -> None:
        self.error_text.value = message
        self.error_text.visible = True
        self.error_text.update()

    def clear_error(self) -> None:
        self.error_text.visible = False
        self.error_text.update()

    def _on_field_change(self, e) -> None:
        self.clear_error()
        self._validate()
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        pattern = r"[a-z0-9_]+"
        return bool(fullmatch(pattern, username))
    
    @staticmethod
    def is_valid_password(password: str) -> bool:
        pattern = r"[A-Za-z0-9!@#$%^&*()_+=\-\[\]{};':\"\\|,.<>/?]+"
        return bool(fullmatch(pattern, password))

    def _validate(self) -> None:
        raise NotImplementedError
