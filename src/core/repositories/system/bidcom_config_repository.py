from abc import ABC, abstractmethod
from pathlib import Path

from src.core.entities.bidcom_workspace import BidcomWorkspaceConfig


class CoreBidcomConfigRepository(ABC):
    @abstractmethod
    def load(self) -> BidcomWorkspaceConfig:
        """Devuelve la config guardada, o los valores por defecto si no existe."""
        ...

    @abstractmethod
    def save(self, config: BidcomWorkspaceConfig) -> None:
        ...

    @abstractmethod
    def location(self) -> Path:
        """Path del archivo de config (para mensajes al usuario)."""
        ...

    @abstractmethod
    def exists(self) -> bool:
        ...
