from src.core.repositories.system.app_launcher_repository import (
    CoreAppLauncherRepository,
)
from src.core.repositories.system.bidcom_config_repository import (
    CoreBidcomConfigRepository,
)
from src.core.repositories.system.clipboard_repository import CoreClipboardRepository
from src.core.repositories.system.clock_repository import CoreClockRepository
from src.core.repositories.system.display_repository import CoreDisplayRepository
from src.core.repositories.system.keyboard_repository import CoreKeyboardRepository
from src.core.repositories.system.media_player_repository import (
    CoreMediaPlayerRepository,
    MediaPlayerAction,
)
from src.core.repositories.system.monitor_config_repository import (
    CoreMonitorConfigRepository,
)
from src.core.repositories.system.screenshot_repository import CoreScreenshotRepository
from src.core.repositories.system.terminal_repository import CoreTerminalRepository
from src.core.repositories.system.window_manager_repository import (
    CoreWindowManagerRepository,
)

__all__ = [
    "CoreAppLauncherRepository",
    "CoreBidcomConfigRepository",
    "CoreClipboardRepository",
    "CoreClockRepository",
    "CoreDisplayRepository",
    "CoreKeyboardRepository",
    "CoreMediaPlayerRepository",
    "MediaPlayerAction",
    "CoreMonitorConfigRepository",
    "CoreScreenshotRepository",
    "CoreTerminalRepository",
    "CoreWindowManagerRepository",
]
