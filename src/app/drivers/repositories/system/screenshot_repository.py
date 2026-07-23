from pathlib import Path

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.system.screenshot_repository import CoreScreenshotRepository


class ScrotScreenshotRepository(CoreScreenshotRepository):
    def __init__(self, command_repo: CoreCommandRepository | None = None) -> None:
        self._command_repo = command_repo or CommandRepository()

    def capture_bbox(self, path_output_png: Path) -> None:
        self._command_repo.run_argv(["scrot", "-q", "100", "-f", "-s", str(path_output_png)])

    def capture_focused(self, path_output_png: Path) -> None:
        self._command_repo.run_argv(["scrot", "-q", "100", "-u", str(path_output_png)])

    def capture_full_screen(self, path_output_png: Path) -> None:
        self._command_repo.run_argv(["scrot", "-q", "100", "-m", str(path_output_png)])
