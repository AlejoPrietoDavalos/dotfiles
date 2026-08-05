"""Puerto: dónde vive el target actual."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.entities.target import Target


class CoreTargetRepository(ABC):
    @abstractmethod
    def get(self) -> Target | None:
        """El target actual, o None si no hay ninguno seteado."""
        ...

    @abstractmethod
    def set(self, target: Target) -> None: ...

    @abstractmethod
    def clear(self) -> None:
        """Idempotente: borrar cuando no hay nada no es un error."""
        ...
