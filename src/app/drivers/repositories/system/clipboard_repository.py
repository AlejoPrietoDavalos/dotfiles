import subprocess
from pathlib import Path

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.system.clipboard_repository import (
    IMAGE_TARGET,
    CoreClipboardRepository,
)

_SELECTION = ["-selection", "clipboard"]


class XclipClipboardRepository(CoreClipboardRepository):
    def __init__(self, command_repo: CoreCommandRepository | None = None) -> None:
        self._command_repo = command_repo or CommandRepository()

    def copy_png_to_clipboard(self, path_png: Path) -> None:
        self._command_repo.run_argv(
            ["xclip", *_SELECTION, "-t", IMAGE_TARGET, "-i", str(path_png)]
        )

    def targets(self) -> list[str]:
        result = subprocess.run(
            ["xclip", *_SELECTION, "-t", "TARGETS", "-o"],
            capture_output=True, text=True, check=False,
        )
        return result.stdout.split()

    def read_text(self) -> str:
        return subprocess.run(
            ["xclip", *_SELECTION, "-o"],
            capture_output=True, text=True, check=False,
        ).stdout

    def write_text(self, text: str) -> None:
        # stdout/stderr a DEVNULL: xclip se queda en segundo plano sirviendo la selección y
        # si hereda una tubería abierta puede quedar bloqueado al escribir en ella.
        subprocess.run(
            ["xclip", *_SELECTION], input=text, text=True, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    def save_png_to(self, path_png: Path) -> bool:
        if IMAGE_TARGET not in self.targets():
            return False
        # Binario: `text=False`. Pedirlo como texto rompe los bytes del PNG.
        result = subprocess.run(
            ["xclip", *_SELECTION, "-t", IMAGE_TARGET, "-o"],
            capture_output=True, check=False,
        )
        if not result.stdout:
            return False
        path_png.parent.mkdir(parents=True, exist_ok=True)
        path_png.write_bytes(result.stdout)
        return True
