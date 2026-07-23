import re

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.system.clock_repository import CoreClockRepository

# Timezone tipo "America/Argentina/Buenos_Aires": solo letras, dígitos, / _ + -
_VALID_TIMEZONE = re.compile(r"^[\w/+-]+$")


class HwclockClockRepository(CoreClockRepository):
    def __init__(self, command_repo: CoreCommandRepository | None = None) -> None:
        self._command_repo = command_repo or CommandRepository()

    def set_timezone(self, timezone: str) -> None:
        if not _VALID_TIMEZONE.match(timezone):
            raise ValueError(f"Timezone inválida: {timezone!r}")
        self._command_repo.run_argv(
            ["sudo", "ln", "-sf", f"/usr/share/zoneinfo/{timezone}", "/etc/localtime"]
        )

    def sync_system_to_hardware(self) -> None:
        self._command_repo.run_argv(["sudo", "hwclock", "--systohc"])
