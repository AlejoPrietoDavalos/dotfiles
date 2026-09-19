#!/usr/bin/env python3
"""Emite el target cada vez que CAMBIA. Fuente para el `deflisten` de eww.

POR QUÉ NO ES UN `defpoll`:

El target cambia unas cinco veces por día. Un poll cada 2s ejecuta el script 43.200 veces
diarias —fork + exec de bash + leer el archivo, ~4 ms cada una— para que 43.195 devuelvan
exactamente lo mismo. Bajarlo a 1s duplica el gasto y sigue sin ser instantáneo.

Este proceso vive una sola vez y hace un `os.stat()` cada 250 ms: microsegundos, sin fork.
Reacciona MÁS RÁPIDO que un poll de 1s y cuesta órdenes de magnitud menos. Es la misma
razón por la que los workspaces usan `bspc subscribe` y no un poll.

Se mira el mtime y no inotify porque `inotify-tools` no es dependencia del repo y un
`stat()` cada cuarto de segundo ya es prácticamente gratis.
"""

from __future__ import annotations

import time
from pathlib import Path

from src.core.constants import path_dotfiles
from src.core.entities.target import Target

_TARGET_PATH = path_dotfiles / "dotfiles" / "target"
_INTERVAL_SECONDS = 0.25


def _read() -> str:
    """El texto que va en la barra. Vacío si no hay target o si el archivo está roto.

    Usa `Target.from_line`, el mismo parser que escribe `FileTargetRepository`: el formato
    del archivo se define en UN solo lugar.
    """
    try:
        line = _TARGET_PATH.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return ""
    target = Target.from_line(line)
    if target is None:
        return ""
    return f"{target.host} ({target.label})" if target.label else target.host


def _stamp() -> tuple[float, int] | None:
    """(mtime, tamaño) del archivo, o None si no existe. Cambia => hay que releer."""
    try:
        stat = _TARGET_PATH.stat()
    except (FileNotFoundError, OSError):
        return None
    return (stat.st_mtime, stat.st_size)


def main() -> int:
    last_stamp = object()   # centinela: fuerza la primera emisión
    last_value = None

    while True:
        stamp = _stamp()
        if stamp != last_stamp:
            last_stamp = stamp
            value = _read()
            # Se emite solo si el VALOR cambió: tocar el archivo sin cambiar el contenido
            # (un `touch`, o reescribir lo mismo) no tiene por qué redibujar la barra.
            if value != last_value:
                last_value = value
                print(value, flush=True)
        time.sleep(_INTERVAL_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
