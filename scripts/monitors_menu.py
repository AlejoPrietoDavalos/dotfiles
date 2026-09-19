#!/usr/bin/env python3
"""Menú interactivo para elegir la distribución de monitores/desktops.

Elegís de qué lado está la notebook y cómo se reparten los desktops. Guarda la
elección (~/.config/bspwm/monitors.json) y la aplica al toque; bspwmrc la vuelve
a aplicar en cada arranque/restart de bspwm.

Solo usa stdlib (input()): no necesita dependencias externas.

Uso: dot monitors   (o  PYTHONPATH=. python3 ./scripts/monitors_menu.py)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app.drivers.repositories.logs import ConfigureLoggingRepository
from src.app.drivers.repositories.system.display_repository import (
    XrandrDisplayRepository,
)
from src.app.drivers.repositories.system.monitor_config_repository import (
    JsonMonitorConfigRepository,
)
from src.app.drivers.repositories.system.window_manager_repository import (
    BspwmWindowManagerRepository,
)
from src.core.entities.monitor_layout import MonitorLayoutConfig
from src.core.use_cases.apply_monitor_layout import ApplyMonitorLayoutService

# (label mostrado, valor guardado)
SIDES = [
    ("Notebook a la izquierda", "left"),
    ("Notebook a la derecha", "right"),
]
DISTRIBUTIONS = [
    ("even    — notebook 1-5, grande 6-0 (parejo)", "even"),
    ("duo     — notebook 1-2, grande 3-0", "duo"),
    ("minimal — notebook sólo el 0, grande 1-9", "minimal"),
    ("pad     — notebook / * - + (pad numérico), grande 1-0", "pad"),
]


def _choose(prompt: str, options: list[tuple[str, str]], current: str) -> str | None:
    """Menú numerado; enter (vacío) mantiene el valor actual."""
    print(f"\n{prompt}")
    for i, (label, value) in enumerate(options, start=1):
        mark = "*" if value == current else " "
        print(f"  {i}. [{mark}] {label}")
    choice = input("Número (enter mantiene el actual): ").strip()
    if not choice:
        return current
    try:
        return options[int(choice) - 1][1]
    except (ValueError, IndexError):
        print("Opción inválida.", file=sys.stderr)
        return None


def main() -> int:
    ConfigureLoggingRepository().configure(log_filename="apply_monitors.log")

    config_repo = JsonMonitorConfigRepository()
    current = config_repo.load()
    print(
        f"Config actual: notebook={current.notebook_side}, "
        f"reparto={current.distribution}"
    )

    side = _choose("¿De qué lado está la notebook?", SIDES, current.notebook_side)
    if side is None:
        return 1
    distribution = _choose(
        "¿Cómo repartir los desktops?", DISTRIBUTIONS, current.distribution
    )
    if distribution is None:
        return 1

    config = MonitorLayoutConfig(notebook_side=side, distribution=distribution)  # type: ignore[arg-type]
    config_repo.save(config)
    print(f"\nGuardado: notebook={config.notebook_side}, reparto={config.distribution}")

    ApplyMonitorLayoutService(
        display_repo=XrandrDisplayRepository(),
        window_manager_repo=BspwmWindowManagerRepository(),
        config_repo=config_repo,
    ).run()
    print("Aplicado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
