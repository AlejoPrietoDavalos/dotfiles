import re

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.system.keyboard_repository import CoreKeyboardRepository

# Layout tipo "latam", "us", "es(dvorak)": letras, dígitos, _ - ( ) ,
_VALID_LAYOUT = re.compile(r"^[\w(),-]+$")


class SetxkbmapKeyboardRepository(CoreKeyboardRepository):
    def __init__(self, command_repo: CoreCommandRepository | None = None) -> None:
        self._command_repo = command_repo or CommandRepository()

    def set_layout(self, layout: str) -> None:
        if not _VALID_LAYOUT.match(layout):
            raise ValueError(f"Layout inválido: {layout!r}")
        self._command_repo.run_argv(["setxkbmap", "-layout", layout])
