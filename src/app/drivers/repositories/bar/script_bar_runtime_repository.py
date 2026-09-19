"""Ejecuta la estrategia de cada barra: sus propios `launch.sh` / `stop.sh`.

Una sola implementación para N barras. Lo que varía no es el código de acá sino QUÉ script
corre, y eso lo dice el `BarSpec` que sale de `programs.json`. Agregar una barra nueva =
una entrada en el JSON + dos scripts. Cero Python.
"""

from __future__ import annotations

import os
import subprocess

from src.core.entities.bar import BarSpec
from src.core.repositories.bar import CoreBarRuntimeRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository


class ScriptBarRuntimeRepository(CoreBarRuntimeRepository):
    def __init__(self, command_repo: CoreCommandRepository) -> None:
        self._command_repo = command_repo

    def is_available(self, bar: BarSpec) -> bool:
        """Instalada = el binario existe Y su config está desplegada.

        Las dos condiciones importan: el paquete sin config no arranca, y la config sin
        paquete tampoco. Chequear solo una da un 'disponible' que después falla al lanzar.
        """
        return (
            self._command_repo.command_exists(bar.binary)
            and bar.path_launch.is_file()
            and bar.path_stop.is_file()
        )

    def launch(self, bar: BarSpec) -> None:
        """Arranca en segundo plano y desacoplada de esta sesión.

        `start_new_session` la saca del grupo de procesos del que la llamó: si no, matar la
        terminal (o que `dot` termine) se lleva la barra puesta.
        """
        subprocess.Popen(
            [str(bar.path_launch)],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={**os.environ},
        )

    def stop(self, bar: BarSpec) -> None:
        """Para la barra. Idempotente: parar algo que no corre no es un error."""
        self._command_repo.run_argv_quiet([str(bar.path_stop)])
