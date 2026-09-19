import subprocess
import shutil

from src.core.repositories.shell.command_repository import CoreCommandRepository


class CommandRepository(CoreCommandRepository):
    def run_argv(self, argv: list[str]) -> None:
        subprocess.run(argv, check=True)

    def run_argv_capture(self, argv: list[str]) -> str:
        completed = subprocess.run(argv, check=True, text=True, capture_output=True)
        return completed.stdout.strip()

    def run_argv_quiet(self, argv: list[str]) -> int:
        return subprocess.run(
            argv,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode

    def command_exists(self, name: str) -> bool:
        return shutil.which(name) is not None
