"""Estado de la barra activa en `~/.config/dotfiles/state.json`.

Fuera del repo a propósito: es una preferencia POR MÁQUINA. Ver `CoreBarStateRepository`.

Toda lectura es tolerante a fallos — archivo ausente, JSON roto, tipo inesperado devuelven
un estado vacío y el caso de uso cae al default. Un estado corrupto no puede dejarte sin
barra.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path

from src.core.constants import path_dotfiles
from src.core.entities.bar import BarName
from src.core.repositories.bar import CoreBarStateRepository

_STATE_PATH = path_dotfiles / "dotfiles" / "state.json"
_KEY = "bar"

# Cualquier valor que pueda salir de `json.loads`. Se usa para las claves que este
# repositorio NO conoce y solo tiene que devolver intactas: no puede afirmar nada sobre su
# forma, pero tampoco hace falta `Any` — el conjunto de tipos posibles de JSON es cerrado.
JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


@dataclass(frozen=True)
class _State:
    """El contenido de `state.json`, tipado.

    `unknown_keys` NO es un detalle: el archivo es el estado de los dotfiles en general, no
    solo de la barra. Sin preservarlas, la primera vez que otra feature guarde algo ahí un
    `dot bar use` se lo borraría en silencio — el bug clásico de leer un archivo compartido
    a un modelo cerrado y volver a escribirlo.
    """

    bar: BarName | None = None
    unknown_keys: dict[str, JsonValue] = field(default_factory=dict)

    @classmethod
    def from_json(cls, raw: JsonValue) -> _State:
        """Nunca levanta: un archivo corrupto es un estado vacío, no una excepción."""
        if not isinstance(raw, dict):
            return cls()
        selected = raw.get(_KEY)
        return cls(
            bar=selected if isinstance(selected, str) and selected else None,
            unknown_keys={key: value for key, value in raw.items() if key != _KEY},
        )

    def to_json(self) -> dict[str, JsonValue]:
        data: dict[str, JsonValue] = dict(self.unknown_keys)
        if self.bar is not None:
            data[_KEY] = self.bar
        return data


class JsonBarStateRepository(CoreBarStateRepository):
    def __init__(self, path_state: Path = _STATE_PATH) -> None:
        self._path = path_state

    def _read(self) -> _State:
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return _State()
        return _State.from_json(raw)

    def get_selected(self) -> BarName | None:
        return self._read().bar

    def set_selected(self, name: BarName) -> None:
        state = replace(self._read(), bar=name)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(state.to_json(), indent=2) + "\n", encoding="utf-8"
        )
