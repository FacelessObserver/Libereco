import flet as ft
from asyncio import create_task, get_event_loop
from ...sources.styles import Colors, Sizes

class SearchField(ft.TextField):
    def __init__(self, on_search, on_empty = None, on_focus = None, on_blur = None):
        super().__init__(
            hint_text = "Search",
            prefix_icon = ft.Icons.SEARCH,
            border_radius = Sizes.BORDER_RADIUS_LARGE,
            border_color = Colors.BACKGROUND_LIGHT,
            focused_border_color = Colors.PRIMARY,
            bgcolor = Colors.BACKGROUND_LIGHT,
            color = Colors.PRIMARY,
            cursor_color = Colors.PRIMARY,
            text_size = 14,
            content_padding = ft.padding.only(
                left = Sizes.PADDING_MEDIUM,
                right = Sizes.PADDING_MEDIUM,
                top = Sizes.PADDING_SMALL,
                bottom = Sizes.PADDING_SMALL
            ),
            expand = True,
            on_change = self._on_change,
            on_focus = self._handle_focus,
            on_blur = self._handle_blur
        )
        self.on_blur_callback = on_blur
        self.on_search = on_search
        self.on_empty = on_empty
        self.on_focus_callback = on_focus
        self.search_delay = 0.35
        self._timer = None

    async def _handle_blur(self, e):
        if self.on_blur_callback:
            await self.on_blur_callback(e)

    async def _handle_focus(self, e):
        if self.on_focus_callback:
            await self.on_focus_callback()

    async def _on_change(self, e):
        query = self.value.strip()
        if self._timer:
            self._timer.cancel()
        if not query:
            if self.on_empty:
                await self.on_empty()
            return
        loop = get_event_loop()
        self._timer = loop.call_later(
            self.search_delay,
            lambda: create_task(
                self._perform_search(query)
            )
        )

    async def _perform_search(self, query: str):
        if self.on_search:
            await self.on_search(query)
