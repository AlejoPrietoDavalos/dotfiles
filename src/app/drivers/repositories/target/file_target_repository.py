"""El target en `~/.config/dotfiles/target`.

UN archivo de texto de UNA línea, y no dentro de `state.json`, por una razón concreta: el
módulo de la barra lo lee cada 2 segundos. Un `.json` obligaría a arrancar Python (o a
sumar `jq`) en cada poll; una línea de texto la lee `read` de bash sin dependencias.

El formato es contrato compartido con `scripts/target-status.sh`, que es el otro lector.
Está definido en `Target.to_line()` / `Target.from_line()`.
"""

from __future__ import annotations

from pathlib import Path

from src.core.constants import path_dotfiles
from src.core.entities.target import Target
from src.core.repositories.target import CoreTargetRepository

_TARGET_PATH = path_dotfiles / "dotfiles" / "target"


class FileTargetRepository(CoreTargetRepository):
    def __init__(self, path_target: Path = _TARGET_PATH) -> None:
        self._path = path_target

    def get(self) -> Target | None:
        try:
            line = self._path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            return None
        return Target.from_line(line)

    def set(self, target: Target) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(target.to_line() + "\n", encoding="utf-8")

    def clear(self) -> None:
        self._path.unlink(missing_ok=True)
