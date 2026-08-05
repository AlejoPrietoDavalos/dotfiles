"""Puerto: qué barra eligió ESTA máquina."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.entities.bar import BarName


class CoreBarStateRepository(ABC):
    """El estado vive fuera del repo, por máquina.

    Es una preferencia de hardware, no de configuración: la notebook con apt se queda en
    polybar y el desktop Arch usa eww, sin que eso genere un conflicto de git ni un commit
    de ida y vuelta cada vez que se cambia.
    """

    @abstractmethod
    def get_selected(self) -> BarName | None:
        """La barra elegida, o None si nunca se eligió (o el estado está corrupto)."""
        ...

    @abstractmethod
    def set_selected(self, name: BarName) -> None: ...
