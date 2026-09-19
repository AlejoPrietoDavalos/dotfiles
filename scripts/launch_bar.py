#!/usr/bin/env python3
"""Arranca la barra de estado activa. Lo llama bspwmrc al iniciar sesión.

Es el punto de entrada ÚNICO de la barra: bspwmrc apunta acá y no vuelve a cambiar.
Cambiar de barra (`dot bar use eww`) solo reescribe el estado; el arranque sigue siendo
esta misma línea. Antes bspwmrc llamaba a `~/.config/polybar/launch.sh` directo, y cambiar
de barra habría implicado reinstalar la config de bspwm.

El fallback (barra elegida no instalada, estado corrupto) lo resuelve `ManageBarService`,
no este script: la misma garantía vale para el CLI y para el arranque.
"""

from src.app.drivers.repositories.bar import build_manage_bar_service
from src.app.drivers.repositories.logs import ConfigureLoggingRepository


def main() -> int:
    # Con log a archivo a propósito: si la barra no levanta al iniciar sesión no hay dónde
    # leer el error — bspwmrc corre sin terminal adjunta.
    ConfigureLoggingRepository().configure(log_filename="launch_bar.log")
    bar = build_manage_bar_service().launch_selected()
    print(f"[bar] {bar.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
