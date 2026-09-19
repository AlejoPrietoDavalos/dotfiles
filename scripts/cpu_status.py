#!/usr/bin/env python3
"""Uso de CPU: porcentaje total + una barra por core.

Reemplaza a `internal/cpu` de polybar, que daba esto gratis (incluido el `ramp-coreload`).
Se muestrea /proc/stat dos veces porque el archivo trae CONTADORES ACUMULADOS desde el
boot: una sola lectura da el promedio histórico, no el uso actual.

Salida: "CPU  42%  ▂▄▁█▃▂▁▁"   (--format ramp, default)
        "42"                    (--format percent, para barras/tooltips)

MODO `--watch`: emite una línea por intervalo hasta que lo maten. Es el que usa eww, y no
es una comodidad — es un requisito de rendimiento.

    eww atiende TODOS los `defpoll` y lee el stdout de TODOS los `deflisten` en un solo
    hilo, y cada `defpoll` corre su script de forma BLOQUEANTE. Con este script como
    `defpoll`, el `time.sleep()` del muestreo dormía ese hilo compartido 250 ms de cada
    1000, y durante esa ventana la línea que `bspwm_workspaces.py` ya había emitido se
    quedaba esperando en el pipe. Se veía como un delay intermitente al cambiar de
    escritorio: medido, la latencia del cambio saltaba de ~50 ms a ~200 ms en 1 de cada 3
    cambios — justo el 25 % de duty cycle del sleep.

    Como `deflisten` el sleep pasa a ocurrir DENTRO de este proceso, que es propio y no le
    importa a nadie. eww solo lee líneas ya listas y nunca se bloquea.

    Corolario para futuros módulos: si un script tarda, va como `deflisten`, no como
    `defpoll`. El costo no lo paga el módulo, lo paga la barra entera.
"""

from __future__ import annotations

import argparse
import time

_RAMP = "▁▂▃▄▅▆▇█"
_SAMPLE_SECONDS = 0.25


def _read_cpu_times() -> list[tuple[int, int]]:
    """(idle, total) por línea 'cpuN' de /proc/stat. El índice 0 es el agregado."""
    times: list[tuple[int, int]] = []
    with open("/proc/stat", encoding="utf-8") as handle:
        for line in handle:
            if not line.startswith("cpu"):
                break
            fields = [int(value) for value in line.split()[1:]]
            # idle = idle + iowait: el CPU no estaba trabajando en ninguno de los dos.
            idle = fields[3] + (fields[4] if len(fields) > 4 else 0)
            times.append((idle, sum(fields)))
    return times


def _percentages(before: list[tuple[int, int]], after: list[tuple[int, int]]) -> list[float]:
    """Uso por CPU entre dos lecturas de contadores."""
    percentages: list[float] = []
    for (idle_0, total_0), (idle_1, total_1) in zip(before, after):
        delta_total = total_1 - total_0
        if delta_total <= 0:
            percentages.append(0.0)
            continue
        delta_idle = idle_1 - idle_0
        percentages.append(100.0 * (delta_total - delta_idle) / delta_total)
    return percentages


def _render(usage: list[float], fmt: str) -> str:
    if not usage:
        return "CPU N/A"
    total = usage[0]
    if fmt == "percent":
        return f"{total:.0f}"
    cores = usage[1:] or [total]
    ramp = "".join(_RAMP[min(int(value / 100 * len(_RAMP)), len(_RAMP) - 1)] for value in cores)
    return f"CPU {total:3.0f}%  {ramp}"


def _watch(fmt: str, interval: float) -> None:
    """Una línea por intervalo, para siempre.

    La PRIMERA muestra usa la ventana corta de `_SAMPLE_SECONDS` para que la barra se
    pueble enseguida en vez de arrancar vacía un segundo entero. De ahí en adelante el
    delta se toma contra la lectura anterior, o sea sobre el intervalo COMPLETO: sale
    gratis (el sleep ya estaba) y promedia mejor que un pantallazo de 250 ms.
    """
    before = _read_cpu_times()
    time.sleep(min(_SAMPLE_SECONDS, interval))
    while True:
        after = _read_cpu_times()
        print(_render(_percentages(before, after), fmt), flush=True)
        before = after
        time.sleep(interval)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("ramp", "percent"), default="ramp")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="emitir una línea por intervalo hasta recibir una señal (modo deflisten)",
    )
    parser.add_argument("--interval", type=float, default=1.0, help="segundos entre líneas con --watch")
    args = parser.parse_args()

    if args.watch:
        try:
            _watch(args.format, args.interval)
        except (KeyboardInterrupt, BrokenPipeError):
            # BrokenPipeError = eww cerró el pipe al recargar o al bajar el daemon. Es la
            # forma NORMAL de terminar en modo watch, no un error que valga reportar.
            pass
        return 0

    before = _read_cpu_times()
    time.sleep(_SAMPLE_SECONDS)
    print(_render(_percentages(before, _read_cpu_times()), args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
