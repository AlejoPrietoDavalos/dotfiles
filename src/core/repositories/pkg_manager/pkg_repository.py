from abc import ABC, abstractmethod

class CoreBasePkgRepository(ABC):
    @property
    @abstractmethod
    def manager_name(self) -> str:
        ...

    @abstractmethod
    def install(self, pkg_names: list[str], program_name: str | None = None) -> None:
        ...

    @abstractmethod
    def uninstall(self, pkg_names: list[str], program_name: str | None = None) -> None:
        ...

    @abstractmethod
    def manager_exists(self) -> bool:
        """True si el package manager está disponible en esta máquina."""
        ...

    @abstractmethod
    def is_installed(self, pkg_names: list[str]) -> bool:
        """True si todos los paquetes están instalados."""
        ...
