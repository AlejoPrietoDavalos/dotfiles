import re

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.system.display_repository import CoreDisplayRepository

_ACTIVE_GEOMETRY = re.compile(r"\d+x\d+\+\d+\+\d+")


class XrandrDisplayRepository(CoreDisplayRepository):
    def __init__(self, command_repo: CoreCommandRepository | None = None) -> None:
        self._command_repo = command_repo or CommandRepository()

    def _query(self) -> str:
        try:
            return self._command_repo.run_capture("xrandr --query")
        except Exception:
            return ""

    def _outputs(self, *, connected: bool, only_active: bool = False) -> list[str]:
        outputs: list[str] = []
        for line in self._query().splitlines():
            if " connected" not in line:
                continue
            if (" disconnected" in line) is connected:
                continue
            parts = line.split()
            if not parts:
                continue
            if only_active and not any(
                _ACTIVE_GEOMETRY.search(token) for token in parts[1:]
            ):
                continue
            outputs.append(parts[0].strip())
        return outputs

    def list_connected_outputs(self) -> list[str]:
        return self._outputs(connected=True)

    def list_active_outputs(self) -> list[str]:
        return self._outputs(connected=True, only_active=True)

    def list_stale_outputs(self) -> list[str]:
        return self._outputs(connected=False, only_active=True)

    def disable_outputs(self, outputs: list[str]) -> None:
        if not outputs:
            return
        cmd_parts = ["xrandr"]
        for output in outputs:
            cmd_parts.extend(["--output", output, "--off"])
        self._command_repo.run(" ".join(cmd_parts))

    def enable_outputs_auto(self, outputs: list[str]) -> None:
        if not outputs:
            return
        cmd_parts = ["xrandr"]
        prev: str | None = None
        for output in outputs:
            cmd_parts.extend(["--output", output, "--auto"])
            if prev:
                cmd_parts.extend(["--right-of", prev])
            prev = output
        self._command_repo.run(" ".join(cmd_parts))
