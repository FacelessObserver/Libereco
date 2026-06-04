from typing import Callable, Awaitable
from .auth_base import AuthBase

class Register(AuthBase):
    def __init__(
        self,
        on_register_success: Callable[[str, str, str], Awaitable[None]],
        on_switch_to_login: Callable[[], Awaitable[None]]
    ):
        super().__init__()

        self.on_success = on_register_success
        self.on_switch = on_switch_to_login

        self.username_field = self.create_text_field(
            label = "*Username"
        )

        self.display_name_field = self.create_text_field(
            label = "Display name"
        )

        self.password_field = self.create_text_field(
            label = "*Password (min — 8 chars)",
            password = True
        )

        self.confirm_password_field = self.create_text_field(
            label = "*Confirm password",
            password = True
        )

        self.submit_button = self.create_submit_button(
            text = "Register",
            on_click = self._on_submit
        )

        self.switch_button = self.create_switch_button(
            text = "Already have account / Sign in",
            on_click = self._on_switch
        )

        self.build_content(
            [
                self.username_field,
                self.display_name_field,
                self.password_field,
                self.confirm_password_field,
                self.submit_button,
                self.switch_button
            ]
        )

    def _validate(self) -> None:
        username = self.username_field.value.strip()
        password = self.password_field.value.strip()
        confirm_password = self.confirm_password_field.value.strip()

        username_valid = self.is_valid_username(username)
        if username and not username_valid:
            self.username_field.height = 85
            self.username_field.error = (
                "Only lowercase english letters, numbers and underscore allowed"
            )
        else:
            self.username_field.height = 50
            self.username_field.error = None

        password_valid = self.is_valid_password(password)
        if password and not password_valid:
            self.password_field.height = 85 
            self.password_field.error = (
                "Only english letters, numbers and special characters allowed"
            )
        else:
            self.password_field.height = 50
            self.password_field.error = None
        
        passwords_match = password == confirm_password
        if not passwords_match:
            self.confirm_password_field.height = 70
            self.confirm_password_field.error = (
                "Passwords do not match"
            )
        else:
            self.confirm_password_field.height = 50
            self.confirm_password_field.error = None


        is_valid = (
            username
            and username_valid
            and len(password) >= 8
            and password_valid
            and passwords_match
        )

        self.set_button_enabled(self.submit_button, is_valid)
        self.update()

    async def _on_switch(self, e) -> None:
        await self.on_switch()

    async def _on_submit(self, e) -> None:
        username = self.username_field.value.strip()
        display_name = self.display_name_field.value.strip()
        password = self.password_field.value.strip()
        confirm_password = self.confirm_password_field.value.strip()

        if not username:
            self.show_error("Enter Username")
            return
        
        if len(password) < 8:
            self.show_error("Minimal password length — 8 chars")
            return
        
        if password != confirm_password:
            self.show_error("Passwords do not match")
            return
        
        await self.on_success(username, display_name or username, password)
