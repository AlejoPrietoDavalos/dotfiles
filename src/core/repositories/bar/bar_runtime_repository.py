"""Puerto de la ESTRATEGIA: cómo se arranca y se para una barra concreta."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.entities.bar import BarSpec


class CoreBarRuntimeRepository(ABC):
    """Opera una barra sin saber cuál es.

    Éste es el punto de variación del slot: polybar itera monitores con `$MONITOR`, eww
    levanta un daemon y abre ventanas. El caso de uso llama siempre a los mismos tres
    métodos y no sabe (ni le importa) cuál de las dos está detrás.
    """

    @abstractmethod
    def is_available(self, bar: BarSpec) -> bool:
        """¿Está instalada EN ESTA MÁQUINA? (binario presente + scripts en su lugar)"""
        ...

    @abstractmethod
    def launch(self, bar: BarSpec) -> None: ...

    @abstractmethod
    def stop(self, bar: BarSpec) -> None: ...
