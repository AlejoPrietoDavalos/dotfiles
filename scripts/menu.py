#!/usr/bin/env python3
"""Menú interactivo para instalar/desinstalar programas del kit de dotfiles.

Lee la lista de programas del loader (programs.json) y ofrece un checkbox para
elegir cuáles, más una acción a aplicar. Reusa ProgramActions: no duplica lógica.

Uso: make menu   (o  PYTHONPATH=. python3 ./scripts/menu.py)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import questionary
except ImportError:
    print(
        "Falta la dependencia 'questionary'. Instalala con:\n"
        "  pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1)

from src.app.drivers.repositories.logs import ConfigureLoggingRepository
from src.app.drivers.repositories.programs import (
    ProgramInstallerRepository,
    ProgramLoaderRepository,
)
from src.core.use_cases.program_actions import ProgramActions

# (label mostrado, action que entiende ProgramActions.run)
ACTIONS = [
    ("Instalar (paquetes + archivos)", "install"),
    ("Instalar solo archivos", "install-files"),
    ("Desinstalar (archivos + paquetes)", "uninstall"),
    ("Desinstalar solo archivos", "uninstall-files"),
]


def main() -> int:
    ConfigureLoggingRepository().configure(log_filename="menu.log")

    loader = ProgramLoaderRepository()
    actions = ProgramActions(
        program_loader_repo=loader,
        program_installer_repo=ProgramInstallerRepository(),
    )

    programs = sorted(loader.list_programs())

    action_label = questionary.select(
        "¿Qué acción querés aplicar?",
        choices=[label for label, _ in ACTIONS],
    ).ask()
    if action_label is None:
        return 0
    action = dict((label, act) for label, act in ACTIONS)[action_label]

    selected = questionary.checkbox(
        "Seleccioná programas (espacio para marcar, enter para confirmar):",
        choices=programs,
    ).ask()
    if not selected:
        print("No se seleccionó ningún programa.")
        return 0

    if not questionary.confirm(
        f"Vas a '{action}' sobre: {', '.join(selected)}. ¿Confirmás?"
    ).ask():
        print("Cancelado.")
        return 0

    for program in selected:
        print(f">> {action} {program}")
        actions.run(action=action, program=program)

    print("Listo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
