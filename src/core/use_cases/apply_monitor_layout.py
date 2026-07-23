import time

from src.core.repositories.system.display_repository import CoreDisplayRepository
from src.core.repositories.system.window_manager_repository import (
    CoreWindowManagerRepository,
)


DESKTOPS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]


def split_even(items: list[str], parts: int) -> list[list[str]]:
    if parts <= 0:
        return []
    base, extra = divmod(len(items), parts)
    chunks: list[list[str]] = []
    index = 0
    for part in range(parts):
        size = base + (1 if part >= (parts - extra) and extra > 0 else 0)
        chunks.append(items[index : index + size])
        index += size
    return chunks


class ApplyMonitorLayoutService:
    def __init__(
        self,
        display_repo: CoreDisplayRepository,
        window_manager_repo: CoreWindowManagerRepository,
        reverse_monitor_layout: bool = True,
    ) -> None:
        self._display_repo = display_repo
        self._window_manager_repo = window_manager_repo
        self._reverse_monitor_layout = reverse_monitor_layout

    def run(self) -> None:
        self._ensure_connected_outputs_enabled()
        monitors = self._resolve_active_monitors()
        if not monitors:
            return

        target_monitors = monitors[: len(DESKTOPS)]
        chunks = split_even(DESKTOPS, len(target_monitors))
        for monitor, desktops in zip(target_monitors, chunks):
            self._window_manager_repo.set_monitor_desktops(monitor, desktops)

    def _ensure_connected_outputs_enabled(self) -> None:
        connected = self._display_repo.list_connected_outputs()
        if not connected:
            return
        target_layout = list(reversed(connected)) if self._reverse_monitor_layout else connected
        active = set(self._display_repo.list_active_outputs())
        if any(output not in active for output in connected):
            self._display_repo.enable_outputs_auto(target_layout)
            time.sleep(0.2)
            return

        self._display_repo.enable_outputs_auto(target_layout)
        time.sleep(0.2)

    def _resolve_active_monitors(self) -> list[str]:
        bspwm_monitors = self._window_manager_repo.list_monitors()
        if not bspwm_monitors:
            return []
        xrandr_active = self._display_repo.list_active_outputs()
        if not xrandr_active:
            return list(reversed(bspwm_monitors)) if self._reverse_monitor_layout else bspwm_monitors
        ordered = [m for m in xrandr_active if m in bspwm_monitors]
        base = ordered or bspwm_monitors
        return list(reversed(base)) if self._reverse_monitor_layout else base


# Backward compatibility while migrating call sites.
ApplyMonitorLayout = ApplyMonitorLayoutService
