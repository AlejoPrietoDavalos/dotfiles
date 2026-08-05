from abc import ABC, abstractmethod

from src.core.entities.program_config import Packages


class CorePkgManagerFactoryRepository(ABC):
    @abstractmethod
    def install(self, pkgs: Packages, program_name: str | None = None) -> None:
        ...

    @abstractmethod
    def uninstall(self, pkgs: Packages, program_name: str | None = None) -> None:
        ...

    @abstractmethod
    def is_installed(self, pkgs: Packages) -> bool | None:
        """Estado de instalación consultando el sistema en vivo.

        True/False si algún manager de los specs existe en esta máquina;
        None si ninguno aplica (ej. spec solo-yay en una máquina sin yay).
        """
        ...
