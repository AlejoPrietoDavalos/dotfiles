from abc import ABC, abstractmethod
from pathlib import Path


class CoreShellRcfileRepository(ABC):
    """Rcfiles generados para arrancar una shell interactiva ya preparada.

    Sirve a cualquier terminal: componer el rcfile no depende del emulador.
    """

    @abstractmethod
    def rcfile_for(self, activate_script: Path) -> Path:
        """Devuelve un rcfile que sourcea el rc del usuario y ``activate_script``."""
        ...
