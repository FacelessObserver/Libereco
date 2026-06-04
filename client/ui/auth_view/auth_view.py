import flet as ft
from asyncio import sleep
from .login import Login
from .register import Register

class AuthView(ft.Container):
    def __init__(self, on_login, on_register):
        super().__init__()

        self.login = Login(
            on_login_success = on_login,
            on_switch_to_register = self._switch_to_register
        )

        self.register = Register(
            on_register_success = on_register,
            on_switch_to_login = self._switch_to_login
        )

        self.content = self.login

        self.fade_duration = 500
        self.opacity = 1.0
        self.animate_opacity = ft.Animation(
            duration = self.fade_duration,
            curve = ft.AnimationCurve.EASE_IN_OUT
        )

    async def _switch_to_register(self) -> None:
        await self._switch_to(self.register)
    
    async def _switch_to_login(self) -> None:
        await self._switch_to(self.login)

    async def _switch_to(self, target) -> None:
        if self.content is target:
            return
        
        self.opacity = 0
        self.update()
        await sleep(self.fade_duration / 1000)
        self.content = target
        self.opacity = 1.0
        self.update()
