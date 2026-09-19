#!/usr/bin/env python3
"""Traza de foco de bspwm, para cazar el bug del `super+shift+N` que "no hace nada".

El síntoma es intermitente: a veces, después de pasar por un desktop, mandar la ventana a
otro escritorio no hace nada. La hipótesis a descartar es que en ese momento bspwm no tenga
NINGÚN nodo enfocado — `bspc node -d` sin selector explícito opera sobre el nodo enfocado,
así que sin foco es un no-op silencioso, que es exactamente "la tecla no responde".

Uso:
    scripts/focus_trace.py > /tmp/focus.log &
    ... reproducir el bug ...
    grep 'SIN FOCO' /tmp/focus.log

Cada línea es un evento de bspwm con el desktop enfocado, el nodo enfocado y su clase. Las
líneas marcadas `<<< SIN FOCO` son los momentos peligrosos: si apretás `super+shift+N` ahí,
no pasa nada.
"""

from __future__ import annotations

import subprocess
import sys
import time


def _run(args: list[str]) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=2).stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def _window_class(node_id: str) -> str:
    """WM_CLASS del nodo, para saber QUÉ ventana tiene el foco (y no solo su id)."""
    out = _run(["xprop", "-id", node_id, "WM_CLASS"])
    return out.split("= ", 1)[1] if "= " in out else "?"


def snapshot(event: str) -> str:
    desktop = _run(["bspc", "query", "-D", "-d", "focused", "--names"])
    node = _run(["bspc", "query", "-N", "-n", "focused"])
    stamp = time.strftime("%H:%M:%S")

    if not node:
        occupied = _run(["bspc", "query", "-N", "-d", "focused"]).split()
        # Que el desktop TENGA ventanas y aun así no haya foco es el caso patológico: hay
        # algo para mover y `bspc node -d` igual no va a hacer nada.
        marca = "<<< SIN FOCO (¡y el desktop tiene ventanas!)" if occupied else "<<< sin foco (desktop vacío, normal)"
        return f"{stamp}  {event:<20} desktop={desktop:<3} nodo=(ninguno)  {marca}"

    return f"{stamp}  {event:<20} desktop={desktop:<3} nodo={node} {_window_class(node)}"


def main() -> int:
    print(snapshot("INICIO"), flush=True)

    with subprocess.Popen(
        ["bspc", "subscribe", "desktop_focus", "node_focus", "node_transfer", "node_remove"],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    ) as proc:
        assert proc.stdout is not None
        for line in iter(proc.stdout.readline, ""):
            event = line.split()[0] if line.split() else "?"
            print(snapshot(event), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, BrokenPipeError):
        sys.exit(0)
