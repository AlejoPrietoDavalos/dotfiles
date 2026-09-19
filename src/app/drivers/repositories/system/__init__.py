from src.app.drivers.repositories.system.app_launcher_repository import (
    LinuxAppLauncherRepository,
)
from src.app.drivers.repositories.system.bidcom_config_repository import (
    JsonBidcomConfigRepository,
)
from src.app.drivers.repositories.system.clipboard_repository import (
    XclipClipboardRepository,
)
from src.app.drivers.repositories.system.clock_repository import HwclockClockRepository
from src.app.drivers.repositories.system.display_repository import XrandrDisplayRepository
from src.app.drivers.repositories.system.keyboard_repository import (
    SetxkbmapKeyboardRepository,
)
from src.app.drivers.repositories.system.media_player_repository import (
    PlayerctlMediaPlayerRepository,
)
from src.app.drivers.repositories.system.monitor_config_repository import (
    JsonMonitorConfigRepository,
)
from src.app.drivers.repositories.system.screenshot_repository import (
    ScrotScreenshotRepository,
)
from src.app.drivers.repositories.system.terminal_repository import (
    KittyTerminalRepository,
)
from src.app.drivers.repositories.system.window_manager_repository import (
    BspwmWindowManagerRepository,
)

__all__ = [
    "LinuxAppLauncherRepository",
    "JsonBidcomConfigRepository",
    "XclipClipboardRepository",
    "HwclockClockRepository",
    "XrandrDisplayRepository",
    "SetxkbmapKeyboardRepository",
    "PlayerctlMediaPlayerRepository",
    "JsonMonitorConfigRepository",
    "ScrotScreenshotRepository",
    "KittyTerminalRepository",
    "BspwmWindowManagerRepository",
]
