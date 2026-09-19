from abc import ABC, abstractmethod
from pathlib import Path


class CoreAppLauncherRepository(ABC):
    """Lanzar procesos de escritorio desacoplados de la CLI y consultarlos."""

    @abstractmethod
    def launch_detached(self, argv: list[str], cwd: Path | None = None) -> None:
        """Lanza un proceso que sobrevive a la CLI (sesión propia, sin stdout)."""
        ...

    @abstractmethod
    def is_process_running(self, name: str) -> bool:
        ...

    @abstractmethod
    def is_user_service_active(self, unit: str) -> bool:
        ...

    @abstractmethod
    def start_user_service(self, unit: str) -> None:
        ...
