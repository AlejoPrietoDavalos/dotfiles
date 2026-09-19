"""Composición del servicio de barra: un solo lugar donde se arma el grafo.

Existe porque hay DOS entradas al mismo caso de uso — el CLI (`dot bar ...`) y el arranque
de la sesión (`scripts/launch_bar.py`, que llama bspwmrc) — y el wiring de los tres
repositorios no puede vivir duplicado: el día que se agregue una dependencia, una de las
dos entradas se olvida y el bug aparece solo en el arranque, que es donde peor se
diagnostica.
"""

from __future__ import annotations

from src.app.drivers.repositories.bar.json_bar_catalog_repository import (
    JsonBarCatalogRepository,
)
from src.app.drivers.repositories.bar.json_bar_state_repository import (
    JsonBarStateRepository,
)
from src.app.drivers.repositories.bar.script_bar_runtime_repository import (
    ScriptBarRuntimeRepository,
)
from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.use_cases.manage_bar import ManageBarService


def build_manage_bar_service() -> ManageBarService:
    """El caso de uso con sus drivers reales, listo para usar."""
    return ManageBarService(
        catalog_repo=JsonBarCatalogRepository(),
        state_repo=JsonBarStateRepository(),
        runtime_repo=ScriptBarRuntimeRepository(CommandRepository()),
    )
