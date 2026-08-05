#!/usr/bin/env python3
"""Traduce `bspc subscribe report` a JSON para el `deflisten` de eww.

Es LA pieza de la migración polybar → eww: polybar trae `internal/bspwm` y te da esto
gratis; en eww hay que parsear el reporte crudo.

FORMATO DEL REPORTE (una línea por evento, campos separados por ':'):

    WmeDP-2:f1:o2:f3:f4:O5:LT:TT:G:MHDMI-1-0:o6:f7:f8:f9:O0:LT:TT:G
    ^ prefijo fijo de la línea entera, no de un campo

El primer caracter de cada campo dice qué es, y MAYÚSCULA significa "enfocado":

    M / m   monitor
    O / o   desktop ocupado (tiene ventanas)
    F / f   desktop libre
    U / u   desktop urgente
    L T G   layout, estado, flags → se ignoran

En Python y no en jq a propósito: `jq` no viene instalado y el repo ya es Python-first
(el CLI `dot` y media `scripts/` lo son). Una dependencia de sistema menos.
"""

from __future__ import annotations

import json
import subprocess
import sys

_MONITOR = "Mm"
_DESKTOP = "OoFfUu"
_OCCUPIED = "Oo"
_URGENT = "Uu"


def parse_report(line: str) -> dict[str, list[dict]]:
    """Reporte crudo → {monitor: [{name, focused, occupied, urgent}, ...]}.

    Se agrupa por monitor para que cada barra filtre el suyo: con dos monitores, la barra
    de eDP-2 no tiene que mostrar los desktops de HDMI-1-0.
    """
    monitors: dict[str, list[dict]] = {}
    current: str | None = None

    for field in line.removeprefix("W").split(":"):
        if not field:
            continue
        kind, value = field[0], field[1:]
        if kind in _MONITOR:
            current = value
            monitors.setdefault(value, [])
        elif kind in _DESKTOP and current is not None:
            monitors[current].append(
                {
                    "name": value,
                    "focused": kind.isupper(),
                    "occupied": kind in _OCCUPIED,
                    "urgent": kind in _URGENT,
                }
            )
    return monitors


def emit(line: str) -> None:
    print(json.dumps(parse_report(line), separators=(",", ":")), flush=True)


def main() -> int:
    # Estado inicial: sin esto la barra arranca vacía y no se puebla hasta el primer
    # cambio de foco, que puede tardar minutos.
    try:
        emit(subprocess.run(["bspc", "wm", "-g"], capture_output=True, text=True, check=True).stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("{}", flush=True)
        return 0

    # `bufsize=1` (line buffered) + `iter(readline, "")` en vez de `for line in proc.stdout`.
    #
    # NO son equivalentes, y la diferencia era un bug real: iterar el file object usa un
    # buffer de lectura anticipada de ~8 KB, así que los eventos de bspc se quedaban ahí
    # hasta que se juntara suficiente texto. Se notaba como que cambiar de escritorio a
    # veces actualizaba la barra al instante y a veces no pasaba nada — el retraso dependía
    # de cuántos eventos faltaran para llenar el buffer, no del tiempo.
    #
    # `readline()` devuelve apenas hay una línea completa, que es lo que hace falta cuando
    # la fuente EMPUJA eventos y no se sabe cuándo llega el próximo.
    with subprocess.Popen(
        ["bspc", "subscribe", "report"],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    ) as proc:
        assert proc.stdout is not None
        for line in iter(proc.stdout.readline, ""):
            emit(line.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
