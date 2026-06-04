from typing import Callable, Awaitable
from .auth_base import AuthBase

class Login(AuthBase):
    def __init__(
        self,
        on_login_success: Callable[[str, str], Awaitable[None]],
        on_switch_to_register: Callable[[], Awaitable[None]]
    ):
        super().__init__()

        self.on_success = on_login_success
        self.on_switch = on_switch_to_register

        self.username_field = self.create_text_field(
            label = "Username"
        )

        self.password_field = self.create_text_field(
            label = "Password",
            password = True
        )

        self.submit_button = self.create_submit_button(
            text = "Sign in",
            on_click = self._on_submit
        )

        self.switch_button = self.create_switch_button(
            text = "Don't have account / Register",
            on_click = self._on_switch
        )
        
        self.build_content(
            [
                self.username_field,
                self.password_field,
                self.submit_button,
                self.switch_button
            ]
        )

    def _validate(self) -> None:
        username = self.username_field.value.strip()
        password = self.password_field.value.strip()

        username_valid = self.is_valid_username(username)
        if username and not username_valid:
            self.username_field.height = 70
            self.username_field.error = "Incorrect username format"
        else:
            self.username_field.height = 50
            self.username_field.error = None
        
        password_valid = self.is_valid_password(password)
        if password and not password_valid:
            self.password_field.height = 70
            self.password_field.error = "Incorrect password format" 
        else:
            self.password_field.height = 50
            self.password_field.error = None

        is_valid = (
            username
            and username_valid
            and len(password) >= 8
            and password_valid
        )

        self.set_button_enabled(self.submit_button, is_valid)
        self.update()

    async def _on_switch(self, e) -> None:
        await self.on_switch()

    async def _on_submit(self, e) -> None:
        username = self.username_field.value.strip()
        password = self.password_field.value.strip()

        if not username or not password:
            self.show_error("Enter Username and Password")
            return

        await self.on_success(username, password)
