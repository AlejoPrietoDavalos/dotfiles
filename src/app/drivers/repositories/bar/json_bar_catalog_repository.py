"""Catálogo de barras leído de `programs.json`.

No hay un archivo aparte: una barra ES un programa del repo que además declara
`"provides": "bar"`. Así `dot install eww` y `dot bar use eww` hablan del mismo dato, y
agregar una barra nueva no toca código Python.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

from src.core.constants import path_repo
from src.core.entities.bar import BarName, BarSpec
from src.core.repositories.bar import CoreBarCatalogRepository

_PROGRAMS_JSON = path_repo / "programs.json"
_SLOT = "bar"

_DEFAULT_LAUNCH = "launch.sh"
_DEFAULT_STOP = "stop.sh"


# --- la forma de `programs.json`, declarada ---------------------------------
#
# `json.loads` devuelve `Any`, así que sin esto el parseo trabaja sobre un dict sin forma:
# `raw.get("files")` no dice qué claves existen ni de qué tipo son, y un typo (`"file"`)
# pasa sin que nada lo note hasta que revienta en runtime.
#
# Son TypedDict y no dataclasses a propósito: describen JSON crudo tal como sale de
# `json.loads` (dicts de verdad, sin instanciar nada), y su chequeo es estático. La
# validación de RUNTIME —lo que falta, lo que está vacío— vive en `_BarEntry`, que es donde
# tiene sentido fallar con un mensaje útil.
#
# `total=False` porque casi todo es opcional; `_RawPackage` sí es total: un paquete sin
# `manager` no es un paquete.


class _RawPackage(TypedDict):
    manager: str
    names: list[str]


class _RawFiles(TypedDict, total=False):
    src: str
    dst: str


class _RawBar(TypedDict, total=False):
    binary: str
    launch: str
    stop: str


class _RawProgram(TypedDict, total=False):
    provides: str
    bar: _RawBar
    files: _RawFiles
    packages: list[_RawPackage]
    deps: list[str]


@dataclass(frozen=True)
class _BarEntry:
    """La forma que tiene una barra DENTRO de `programs.json`.

    Separada de `BarSpec` a propósito: acá viven los strings crudos del JSON con sus
    defaults; allá, el objeto de dominio ya resuelto (rutas absolutas, `~` expandido).

    Existe para que el contrato del JSON esté DECLARADO. Con `.get()` sueltos en medio del
    parseo, un archivo mal escrito no falla: propaga un `None` o un `""` que revienta tres
    capas más adelante, y el error apunta a cualquier lado menos al JSON.

    Representa este bloque:

        "eww": {
          "provides": "bar",
          "bar": { "binary": "eww", "launch": "launch.sh", "stop": "stop.sh" },
          "packages": [{ "manager": "yay", "names": ["eww"] }],
          "files": { "src": "eww", "dst": "~/.config/eww" }
        }
    """

    name: str
    binary: str
    launch: str
    stop: str
    config_dst: str
    managers: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.config_dst:
            raise ValueError(
                f"La barra '{self.name}' tiene 'files' pero sin 'dst': sin su directorio "
                "de config no hay dónde buscar launch/stop."
            )

    @classmethod
    def from_json(cls, name: str, raw: _RawProgram) -> _BarEntry:
        """Raises: ValueError si al programa le falta lo mínimo para ser una barra."""
        files = raw.get("files")
        if files is None:
            raise ValueError(
                f"El programa '{name}' declara provides='{_SLOT}' pero no tiene 'files': "
                "una barra necesita su directorio de config para encontrar launch/stop."
            )

        # `binary` cae al nombre del programa porque casi siempre coinciden (polybar →
        # polybar, eww → eww); declararlo solo hace falta cuando difieren.
        bar = raw.get(_SLOT, {})
        return cls(
            name=name,
            binary=bar.get("binary", name),
            launch=bar.get("launch", _DEFAULT_LAUNCH),
            stop=bar.get("stop", _DEFAULT_STOP),
            config_dst=files.get("dst", ""),
            managers=tuple(spec["manager"] for spec in raw.get("packages", [])),
        )

    def to_spec(self) -> BarSpec:
        """El objeto de dominio, con `~` ya expandido a la home real."""
        return BarSpec(
            name=self.name,
            binary=self.binary,
            config_dir=Path(self.config_dst).expanduser(),
            launch_script=self.launch,
            stop_script=self.stop,
            managers=self.managers,
        )


class JsonBarCatalogRepository(CoreBarCatalogRepository):
    def __init__(self, path_json: Path = _PROGRAMS_JSON) -> None:
        # La anotación es una AFIRMACIÓN, no una validación: `json.loads` no verifica nada.
        # Lo que sí falla con un mensaje útil es `_BarEntry`, más abajo.
        raw: dict[str, _RawProgram] = json.loads(path_json.read_text(encoding="utf-8"))
        self._specs: dict[BarName, BarSpec] = {
            name: _BarEntry.from_json(name, cfg).to_spec()
            for name, cfg in raw.items()
            if cfg.get("provides") == _SLOT
        }
        if not self._specs:
            raise ValueError(
                f"Ningún programa declara provides='{_SLOT}' en {path_json}. "
                "Al menos polybar tiene que hacerlo."
            )

    def list_bars(self) -> list[BarSpec]:
        return sorted(self._specs.values(), key=lambda bar: bar.name)

    def get(self, name: BarName) -> BarSpec:
        if name not in self._specs:
            raise ValueError(
                f"Barra desconocida '{name}'. Disponibles: {sorted(self._specs)}"
            )
        return self._specs[name]
