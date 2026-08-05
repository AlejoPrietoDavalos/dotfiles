"""Puerto: de dónde salen las barras disponibles."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.entities.bar import BarName, BarSpec


class CoreBarCatalogRepository(ABC):
    """Las barras que el repo conoce, con su spec ya resuelta."""

    @abstractmethod
    def list_bars(self) -> list[BarSpec]: ...

    @abstractmethod
    def get(self, name: BarName) -> BarSpec:
        """Raises: ValueError si `name` no es una barra conocida."""
        ...
