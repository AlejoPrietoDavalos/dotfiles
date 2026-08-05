"""Caso de uso: elegir, arrancar y parar la barra de estado.

El contexto del patrón Strategy: acá vive el algoritmo ESTABLE (resolver cuál, validar,
parar la vieja, arrancar la nueva) y la parte que varía se delega en
`CoreBarRuntimeRepository`.

La regla que ordena todo: **nunca se puede quedar sin barra.** Cualquier estado raro
—vacío, corrupto, apuntando a una barra que no está instalada— cae a `DEFAULT_BAR` en vez
de fallar. Fallar acá significa un escritorio sin barra después de un `bspc wm -r`, y eso
se arregla a ciegas.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.entities.bar import DEFAULT_BAR, BarName, BarSpec
from src.core.repositories.bar import (
    CoreBarCatalogRepository,
    CoreBarRuntimeRepository,
    CoreBarStateRepository,
)


class BarNotAvailableError(Exception):
    """La barra existe en el catálogo pero no está instalada en esta máquina."""


@dataclass(frozen=True)
class BarStatus:
    """Una barra tal como se le muestra al usuario en `dot bar list`."""

    name: BarName
    selected: bool
    available: bool
    managers: tuple[str, ...]


class ManageBarService:
    def __init__(
        self,
        catalog_repo: CoreBarCatalogRepository,
        state_repo: CoreBarStateRepository,
        runtime_repo: CoreBarRuntimeRepository,
    ) -> None:
        self._catalog = catalog_repo
        self._state = state_repo
        self._runtime = runtime_repo

    # --- consulta ---------------------------------------------------------

    def resolve(self) -> BarSpec:
        """La barra que corresponde usar ahora mismo, con fallback garantizado.

        Se degrada en dos pasos, y cada uno tapa un escenario real:
          1. estado vacío/desconocido → default (primera instalación, estado borrado)
          2. elegida pero NO instalada → default (clonaste los dotfiles en una máquina
             nueva y todavía no compilaste eww)
        """
        selected = self._state.get_selected()
        if selected is not None:
            try:
                bar = self._catalog.get(selected)
            except ValueError:
                bar = self._catalog.get(DEFAULT_BAR)
            else:
                if self._runtime.is_available(bar):
                    return bar
                bar = self._catalog.get(DEFAULT_BAR)
            return bar
        return self._catalog.get(DEFAULT_BAR)

    def list_status(self) -> list[BarStatus]:
        selected = self.resolve().name
        return [
            BarStatus(
                name=bar.name,
                selected=bar.name == selected,
                available=self._runtime.is_available(bar),
                managers=bar.managers,
            )
            for bar in self._catalog.list_bars()
        ]

    # --- acciones ---------------------------------------------------------

    def use(self, name: BarName, *, restart: bool = True) -> BarSpec:
        """Cambia la barra activa. Falla ANTES de tocar el estado si no se puede.

        Raises:
            ValueError: `name` no es una barra conocida.
            BarNotAvailableError: no está instalada en esta máquina.
        """
        bar = self._catalog.get(name)
        if not self._runtime.is_available(bar):
            raise BarNotAvailableError(
                f"'{bar.name}' no está instalada en esta máquina "
                f"(falta el binario '{bar.binary}' o su config). "
                f"Gestores que la ofrecen: {', '.join(bar.managers) or 'ninguno'}. "
                f"Instalala con: dot install {bar.name}"
            )

        # El estado se escribe DESPUÉS de validar: si esto falla a mitad, la máquina sigue
        # con la barra que andaba, no con una elección que no se puede honrar.
        previous = self.resolve()
        self._state.set_selected(bar.name)

        if restart:
            if previous.name != bar.name:
                self._runtime.stop(previous)
            self._runtime.stop(bar)
            self._runtime.launch(bar)
        return bar

    def launch_selected(self) -> BarSpec:
        """Arranca la barra activa. Es lo que llama bspwm al iniciar sesión."""
        bar = self.resolve()
        self._runtime.stop(bar)
        self._runtime.launch(bar)
        return bar

    def stop_all(self) -> None:
        """Para toda barra conocida que esté instalada.

        Recorre el catálogo entero en vez de solo la activa: si quedó un proceso colgado
        de la barra anterior, también reserva struts y bspwm resta el espacio dos veces.
        """
        for bar in self._catalog.list_bars():
            if self._runtime.is_available(bar):
                self._runtime.stop(bar)
