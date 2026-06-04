import flet as ft

class Colors:
    """Цветовая схема приложения."""

    PRIMARY = "#ffffff"
    PRIMARY_DARK = "#dddddd"
    
    SELECT = "#78b9ff"

    BACKGROUND = "#000000"
    BACKGROUND_LD = "#0A0A0A"
    BACKGROUND_LIGHT = "#1a1a1a"
    BACKGROUND_SUP_LIGHT = "#2a2a2a"

    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#888888"
    TEXT_DISABLED = "#555555"

    MESSAGE_OUTGOING = "#ffffff"
    MESSAGE_INCOMING = "#2a2a2a"

    ONLINE = "#4caf50"
    OFFLINE = "#888888"
    AWAY = "#ff9800"

    ERROR = "#f44336"
    WARNING = "#ff9800"
    SUCCESS = "#4caf50"


class Sizes:
    """Размеры элементов."""
    
    PADDING_SMALL = 8
    PADDING_MEDIUM = 16
    PADDING_LARGE = 24
    
    BORDER_RADIUS_SMALL = 8
    BORDER_RADIUS_MEDIUM = 12
    BORDER_RADIUS_LARGE = 20
    
    FONT_SMALL = 12
    FONT_MEDIUM = 14
    FONT_LARGE = 16
    FONT_TITLE = 20
    FONT_HEADER = 24

ENABLED_BUTTON_STYLE = ft.ButtonStyle(
    bgcolor = Colors.PRIMARY,
    color = Colors.BACKGROUND
)

DISABLED_BUTTON_STYLE = ft.ButtonStyle(
    bgcolor = Colors.BACKGROUND_LD,
    color = Colors.PRIMARY
)

INPUT_STYLE = {
    "border_radius": Sizes.BORDER_RADIUS_MEDIUM,
    "border_color": Colors.PRIMARY_DARK,
    "bgcolor": Colors.BACKGROUND,
    "color": Colors.PRIMARY,
    "cursor_color": Colors.PRIMARY,
    "cursor_width": 1,
    "selection_color": Colors.SELECT,
    "height": 50,
    "content_padding": Sizes.PADDING_MEDIUM
}
