import re

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.system.window_manager_repository import (
    CoreWindowManagerRepository,
)


class BspwmWindowManagerRepository(CoreWindowManagerRepository):
    def __init__(self, command_repo: CoreCommandRepository | None = None) -> None:
        self._command_repo = command_repo or CommandRepository()

    def list_monitors(self) -> list[str]:
        return self._query("bspc query -M --names")

    def set_monitor_desktops(self, monitor: str, desktops: list[str]) -> None:
        if not desktops:
            return
        quoted = " ".join(f"'{d}'" for d in desktops)
        self._command_repo.run(f"bspc monitor '{monitor}' -d {quoted}")

    def list_desktops(self) -> list[str]:
        return self._query("bspc query -D --names")

    def focus_desktop(self, desktop: str) -> None:
        # `%` fuerza selección por nombre (los desktops "1"-"0" son ambiguos).
        self._command_repo.run_argv(["bspc", "desktop", "-f", f"%{desktop}"])

    def list_window_ids(self) -> list[str]:
        return self._query("bspc query -N -n .window")

    def window_class(self, window_id: str) -> list[str]:
        try:
            out = self._command_repo.run_argv_capture(
                ["xprop", "-id", window_id, "WM_CLASS"]
            )
        except Exception:
            return []
        # WM_CLASS(STRING) = "code", "Code"
        return re.findall(r'"([^"]*)"', out)

    def desktop_of_window(self, window_id: str) -> str | None:
        try:
            out = self._command_repo.run_argv_capture(
                ["bspc", "query", "-D", "-n", window_id, "--names"]
            )
        except Exception:
            return None
        return out.strip() or None

    def move_window_to_desktop(self, window_id: str, desktop: str) -> None:
        self._command_repo.run_argv(["bspc", "node", window_id, "-d", f"%{desktop}"])

    def add_one_shot_rule(self, wm_class: str, desktop: str) -> None:
        self._command_repo.run_argv(
            ["bspc", "rule", "-a", wm_class, "-o", f"desktop=%{desktop}", "follow=off"]
        )

    def remove_rules(self, wm_class: str) -> None:
        # Devuelve error si no había regla pendiente: es el caso normal
        # (la one-shot ya se consumió), lo ignoramos.
        self._command_repo.run_argv_quiet(["bspc", "rule", "-r", wm_class])

    def _query(self, cmd: str) -> list[str]:
        try:
            out = self._command_repo.run_capture(cmd)
        except Exception:
            return []
        return [line.strip() for line in out.splitlines() if line.strip()]
