from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.system.media_player_repository import (
    CoreMediaPlayerRepository,
    MediaPlayerAction,
)


class PlayerctlMediaPlayerRepository(CoreMediaPlayerRepository):
    def __init__(self, command_repo: CoreCommandRepository | None = None) -> None:
        self._command_repo = command_repo or CommandRepository()

    def run(self, action: MediaPlayerAction) -> None:
        if action == "previous":
            self.previous()
        elif action == "next":
            self.next()
        elif action == "play_pause":
            self.play_pause()
        elif action == "stop":
            self.stop()
        else:
            raise ValueError(f"Unsupported action: {action}")

    def previous(self) -> None:
        self._command_repo.run_argv_quiet(["playerctl", "previous"])

    def next(self) -> None:
        self._command_repo.run_argv_quiet(["playerctl", "next"])

    def play_pause(self) -> None:
        self._command_repo.run_argv_quiet(["playerctl", "play-pause"])

    def stop(self) -> None:
        self._command_repo.run_argv_quiet(["playerctl", "stop"])
