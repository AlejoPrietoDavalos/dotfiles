"""Dominio de la distribución de monitores/desktops en bspwm.

Dos ejes independientes, ambos elegibles por el usuario:

- ``notebook_side``: de qué lado físico queda la notebook respecto del monitor
  grande. Sólo afecta el orden de ``xrandr`` (--left-of/--right-of); NO remapea
  los números de desktop.
- ``distribution``: qué desktops recibe cada *rol* (notebook / externo). Se
  resuelve con el patrón Strategy, así se pueden agregar repartos nuevos sin
  tocar el caso de uso.

Los números de desktop están pegados al rol, no a la posición: la notebook
siempre tiene los mismos desktops la muevas al lado que la muevas.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, get_args

NotebookSide = Literal["left", "right"]
DistributionName = Literal["even", "duo", "minimal", "pad"]

NOTEBOOK_SIDES: tuple[NotebookSide, ...] = get_args(NotebookSide)
DISTRIBUTION_NAMES: tuple[DistributionName, ...] = get_args(DistributionName)

# Orden canónico de los 10 desktops de bspwm (el "0" es el último).
DESKTOPS: list[str] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

# Desktops extra atados a las teclas superiores del pad numérico (/ * - +).
# En bspwm se llaman n1..n4 (nombres seguros para los selectores `%<name>`);
# polybar los muestra como / * - + vía ws-icon.
PAD_DESKTOPS: list[str] = ["n1", "n2", "n3", "n4"]

# Outputs internos de una notebook (panel del equipo) según su nombre de conector.
_INTERNAL_OUTPUT_RE = re.compile(r"^(eDP|LVDS|DSI)", re.IGNORECASE)


def is_internal_output(name: str) -> bool:
    """True si el nombre de output/monitor corresponde al panel de la notebook."""
    return bool(_INTERNAL_OUTPUT_RE.match(name.strip()))


def split_even(items: list[str], parts: int) -> list[list[str]]:
    """Reparte ``items`` en ``parts`` grupos lo más parejos posible.

    Los grupos más grandes quedan al final (los primeros monitores reciben los
    números bajos cuando la cuenta no es exacta).
    """
    if parts <= 0:
        return []
    base, extra = divmod(len(items), parts)
    chunks: list[list[str]] = []
    index = 0
    for part in range(parts):
        size = base + (1 if part >= (parts - extra) and extra > 0 else 0)
        chunks.append(items[index : index + size])
        index += size
    return chunks


# --------------------------------------------------------------------------- #
#                         Strategy: reparto de desktops                        #
# --------------------------------------------------------------------------- #
class DesktopDistributionStrategy(ABC):
    """Decide qué desktops recibe cada monitor, en función del rol de cada uno."""

    name: DistributionName

    @abstractmethod
    def assign(
        self, notebook: str | None, externals: list[str]
    ) -> dict[str, list[str]]:
        """Devuelve ``{monitor: [desktops]}``.

        ``notebook`` es el nombre del monitor interno (o ``None`` si no hay), y
        ``externals`` los monitores externos en orden.
        """
        ...

    @staticmethod
    def _even_over(monitors: list[str]) -> dict[str, list[str]]:
        chunks = split_even(DESKTOPS, len(monitors))
        return {monitor: chunk for monitor, chunk in zip(monitors, chunks)}


class EvenSplitStrategy(DesktopDistributionStrategy):
    """Reparte los 10 desktops parejo. Con 2 monitores: notebook=1-5, grande=6-0."""

    name = "even"

    def assign(
        self, notebook: str | None, externals: list[str]
    ) -> dict[str, list[str]]:
        monitors = ([notebook] if notebook else []) + externals
        if not monitors:
            return {}
        return self._even_over(monitors)


class NotebookDuoStrategy(DesktopDistributionStrategy):
    """La notebook se queda con "1" y "2"; el resto (3-0) va al/los externos."""

    name = "duo"

    def assign(
        self, notebook: str | None, externals: list[str]
    ) -> dict[str, list[str]]:
        if notebook and externals:
            assignment: dict[str, list[str]] = {notebook: DESKTOPS[:2]}
            rest = DESKTOPS[2:]
            for external, chunk in zip(externals, split_even(rest, len(externals))):
                assignment[external] = chunk
            return assignment
        # Sin externo (sólo notebook) o sin notebook: reparto parejo para no
        # dejar monitores sin desktops.
        monitors = ([notebook] if notebook else []) + externals
        return self._even_over(monitors) if monitors else {}


class NotebookMinimalStrategy(DesktopDistributionStrategy):
    """La notebook se queda sólo con el desktop "0"; el resto (1-9) va al/los externos."""

    name = "minimal"

    def assign(
        self, notebook: str | None, externals: list[str]
    ) -> dict[str, list[str]]:
        if notebook and externals:
            assignment: dict[str, list[str]] = {notebook: [DESKTOPS[-1]]}
            rest = DESKTOPS[:-1]
            for external, chunk in zip(externals, split_even(rest, len(externals))):
                assignment[external] = chunk
            return assignment
        # Sin externo (sólo notebook) o sin notebook: no hay a quién "minimizar",
        # caemos a un reparto parejo para no dejar monitores sin desktops.
        monitors = ([notebook] if notebook else []) + externals
        return self._even_over(monitors) if monitors else {}


class NotebookPadStrategy(DesktopDistributionStrategy):
    """La notebook recibe los 4 desktops del pad (n1-n4); los externos, 1-0.

    Sin externo, la notebook tiene los 14: pad a la izquierda y después 1-0.
    """

    name = "pad"

    def assign(
        self, notebook: str | None, externals: list[str]
    ) -> dict[str, list[str]]:
        # Sin notebook, el primer externo toma su rol (se lleva el pad).
        holder = notebook or (externals[0] if externals else None)
        if holder is None:
            return {}
        rest = [name for name in externals if name != holder]
        if not rest:
            return {holder: [*PAD_DESKTOPS, *DESKTOPS]}
        assignment: dict[str, list[str]] = {holder: list(PAD_DESKTOPS)}
        for external, chunk in zip(rest, split_even(DESKTOPS, len(rest))):
            assignment[external] = chunk
        return assignment


_STRATEGIES: dict[DistributionName, DesktopDistributionStrategy] = {
    strategy.name: strategy
    for strategy in (
        EvenSplitStrategy(),
        NotebookDuoStrategy(),
        NotebookMinimalStrategy(),
        NotebookPadStrategy(),
    )
}


def get_distribution_strategy(name: DistributionName) -> DesktopDistributionStrategy:
    try:
        return _STRATEGIES[name]
    except KeyError:
        raise ValueError(
            f"Distribución desconocida '{name}'. Disponibles: {DISTRIBUTION_NAMES}"
        )


# --------------------------------------------------------------------------- #
#                                  Config                                      #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class MonitorLayoutConfig:
    notebook_side: NotebookSide = "left"
    distribution: DistributionName = "even"

    def __post_init__(self) -> None:
        if self.notebook_side not in NOTEBOOK_SIDES:
            raise ValueError(
                f"notebook_side inválido '{self.notebook_side}'. "
                f"Disponibles: {NOTEBOOK_SIDES}"
            )
        if self.distribution not in DISTRIBUTION_NAMES:
            raise ValueError(
                f"distribution inválido '{self.distribution}'. "
                f"Disponibles: {DISTRIBUTION_NAMES}"
            )

    def to_dict(self) -> dict[str, str]:
        return {
            "notebook_side": self.notebook_side,
            "distribution": self.distribution,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "MonitorLayoutConfig":
        defaults = cls()
        return cls(
            notebook_side=data.get("notebook_side", defaults.notebook_side),  # type: ignore[arg-type]
            distribution=data.get("distribution", defaults.distribution),  # type: ignore[arg-type]
        )
