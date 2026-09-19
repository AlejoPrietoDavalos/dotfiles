from pathlib import Path

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.app.drivers.repositories.shell.rcfile_repository import BashRcfileRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.shell.rcfile_repository import CoreShellRcfileRepository
from src.core.repositories.system.app_launcher_repository import (
    CoreAppLauncherRepository,
)
from src.core.repositories.system.terminal_repository import CoreTerminalRepository


class KittyTerminalRepository(CoreTerminalRepository):
    """Abre kitty (la misma terminal que sxhkd en super+Enter).

    Para activar el venv sin perder el ~/.bashrc se arranca
    ``bash --rcfile <rc> -i`` adentro de kitty; el rcfile lo compone
    ``rcfile_repo``. Los flags son los de kitty: para otra terminal va otro
    driver de ``CoreTerminalRepository``, no un if acá adentro.
    """

    def __init__(
        self,
        launcher_repo: CoreAppLauncherRepository,
        program: str = "kitty",
        command_repo: CoreCommandRepository | None = None,
        rcfile_repo: CoreShellRcfileRepository | None = None,
    ) -> None:
        if Path(program).name != "kitty":
            raise SystemExit(
                f"Este driver solo maneja kitty, no '{program}'. "
                "Poné `terminal.program` en kitty o implementá el driver que falte."
            )
        self._launcher_repo = launcher_repo
        self._program = program
        self._command_repo = command_repo or CommandRepository()
        self._rcfile_repo = rcfile_repo or BashRcfileRepository()

    def open(self, directory: Path, activate_script: Path | None = None) -> None:
        if not self._command_repo.command_exists(self._program):
            raise SystemExit(f"Terminal '{self._program}' no está en PATH.")
        argv = [self._program, "--directory", str(directory)]
        if activate_script:
            rcfile = self._rcfile_repo.rcfile_for(activate_script)
            argv += ["bash", "--rcfile", str(rcfile), "-i"]
        self._launcher_repo.launch_detached(argv)
