from abc import ABC, abstractmethod

from src.core.entities.monitor_layout import MonitorLayoutConfig


class CoreMonitorConfigRepository(ABC):
    @abstractmethod
    def load(self) -> MonitorLayoutConfig:
        """Devuelve la config guardada, o los valores por defecto si no existe."""
        ...

    @abstractmethod
    def save(self, config: MonitorLayoutConfig) -> None:
        ...
