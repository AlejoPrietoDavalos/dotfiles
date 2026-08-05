"""La barra de estado como *slot* intercambiable del escritorio.

Polybar y eww resuelven el mismo problema y no pueden convivir (las dos reservarían
espacio y bspwm restaría el doble). O sea: son ESTRATEGIAS del mismo rol.

Lo que varía entre ellas es cómo se arrancan y se paran — polybar lanza una instancia por
monitor vía `$MONITOR`, eww levanta un daemon y abre ventanas —, y eso no se puede
expresar de forma declarativa sin inventar un mini-lenguaje. Así que cada barra trae sus
propios `launch.sh` / `stop.sh` **dentro de su carpeta de config**, y ese par de scripts ES
la estrategia. `BarSpec` es solo el dato que dice cuál es cuál.

Por qué no clases Python por barra: el repo ya hizo el camino inverso a propósito
(commit f931538, "reemplaza clases por-programa con programs.json declarativo"). Agregar
`PolybarStrategy`/`EwwStrategy` reintroduciría justo lo que se sacó. La variación queda
donde el resto del repo la pone: en `programs.json` + un script.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

BarName = str

# Con qué se queda el sistema si el estado está vacío, corrupto, o pide una barra que en
# esta máquina no existe. Siempre tiene que ser la que está disponible en TODOS los
# gestores de paquetes soportados: es la red que impide quedarse sin barra.
DEFAULT_BAR: BarName = "polybar"


@dataclass(frozen=True)
class BarSpec:
    """Una barra concreta y cómo se la opera."""

    name: BarName
    """Binario que tiene que existir para poder usarla (`polybar`, `eww`)."""
    binary: str
    """Directorio de config ya instalado (`~/.config/polybar`). Es donde viven los scripts."""
    config_dir: Path
    """Nombre del script de arranque, relativo a `config_dir`."""
    launch_script: str
    """Nombre del script de parada, relativo a `config_dir`."""
    stop_script: str
    """Gestores de paquetes que la ofrecen (según `programs.json`). Vacío = ninguno."""
    managers: tuple[str, ...]

    @property
    def path_launch(self) -> Path:
        return self.config_dir / self.launch_script

    @property
    def path_stop(self) -> Path:
        return self.config_dir / self.stop_script

    def is_supported_by(self, manager: str) -> bool:
        """¿Este gestor de paquetes puede instalarla?

        `eww` no está en los repos de Debian/Ubuntu (hay que compilarlo con Rust), así que
        su entrada en `programs.json` no declara `apt`. Eso hace que en apt la barra ni
        siquiera sea ofrecida — no hay lógica por sistema operativo en ningún lado.
        """
        return manager in self.managers
