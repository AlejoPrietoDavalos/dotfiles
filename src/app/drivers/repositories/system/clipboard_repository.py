from pathlib import Path

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.system.clipboard_repository import CoreClipboardRepository


class XclipClipboardRepository(CoreClipboardRepository):
    def __init__(self, command_repo: CoreCommandRepository | None = None) -> None:
        self._command_repo = command_repo or CommandRepository()

    def copy_png_to_clipboard(self, path_png: Path) -> None:
        self._command_repo.run_argv(
            ["xclip", "-selection", "clipboard", "-t", "image/png", "-i", str(path_png)]
        )
