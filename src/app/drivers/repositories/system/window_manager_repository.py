from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.system.window_manager_repository import (
    CoreWindowManagerRepository,
)


class BspwmWindowManagerRepository(CoreWindowManagerRepository):
    def __init__(self, command_repo: CoreCommandRepository | None = None) -> None:
        self._command_repo = command_repo or CommandRepository()

    def list_monitors(self) -> list[str]:
        try:
            out = self._command_repo.run_argv_capture(["bspc", "query", "-M", "--names"])
        except Exception:
            return []
        return [line.strip() for line in out.splitlines() if line.strip()]

    def set_monitor_desktops(self, monitor: str, desktops: list[str]) -> None:
        if not desktops:
            return
        self._command_repo.run_argv(["bspc", "monitor", monitor, "-d", *desktops])
