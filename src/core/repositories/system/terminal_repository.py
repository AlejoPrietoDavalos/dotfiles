from abc import ABC, abstractmethod
from pathlib import Path


class CoreTerminalRepository(ABC):
    @abstractmethod
    def open(self, directory: Path, activate_script: Path | None = None) -> None:
        """Abre una terminal en ``directory``.

        Si ``activate_script`` está definido (``env/bin/activate``), la shell
        interactiva arranca con ese entorno virtual ya activado.
        """
        ...
