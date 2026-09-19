import time

from src.core.entities.monitor_layout import (
    MonitorLayoutConfig,
    get_distribution_strategy,
    is_internal_output,
)
from src.core.repositories.system.display_repository import CoreDisplayRepository
from src.core.repositories.system.monitor_config_repository import (
    CoreMonitorConfigRepository,
)
from src.core.repositories.system.window_manager_repository import (
    CoreWindowManagerRepository,
)


class ApplyMonitorLayoutService:
    """Aplica la distribución elegida de monitores/desktops.

    1. Apaga los outputs desconectados que xrandr dejó encendidos (si no, el WM
       los sigue viendo como monitores y se lleva desktops a la nada).
    2. Ordena físicamente los outputs con xrandr según ``notebook_side``.
    3. Reparte los desktops entre los monitores de bspwm según la estrategia
       de ``distribution`` (pegados al rol: notebook vs externo).
    """

    def __init__(
        self,
        display_repo: CoreDisplayRepository,
        window_manager_repo: CoreWindowManagerRepository,
        config_repo: CoreMonitorConfigRepository,
    ) -> None:
        self._display_repo = display_repo
        self._window_manager_repo = window_manager_repo
        self._config_repo = config_repo

    def run(self) -> None:
        config = self._config_repo.load()
        connected = self._display_repo.list_connected_outputs()
        self._apply_physical_layout(connected, config)
        self._apply_desktop_distribution(connected, config)

    # -- xrandr: ordenar los outputs de izquierda a derecha ------------------ #
    def _apply_physical_layout(
        self, connected: list[str], config: MonitorLayoutConfig
    ) -> None:
        stale = self._display_repo.list_stale_outputs()
        if stale:
            self._display_repo.disable_outputs(stale)
            time.sleep(0.2)
        if not connected:
            return
        notebook, externals = self._classify(connected)
        ordered = self._order_by_side(notebook, externals, config.notebook_side)
        self._display_repo.enable_outputs_auto(ordered)
        time.sleep(0.2)

    # -- bspwm: repartir los desktops por rol -------------------------------- #
    def _apply_desktop_distribution(
        self, connected: list[str], config: MonitorLayoutConfig
    ) -> None:
        monitors = self._live_monitors(connected)
        if not monitors:
            return
        notebook, externals = self._classify(monitors)
        strategy = get_distribution_strategy(config.distribution)
        assignment = strategy.assign(notebook, externals)
        for monitor, desktops in assignment.items():
            self._window_manager_repo.set_monitor_desktops(monitor, desktops)

    # -- helpers ------------------------------------------------------------- #
    def _live_monitors(self, connected: list[str]) -> list[str]:
        """Monitores de bspwm que siguen respaldados por un output conectado.

        Red de seguridad por si el WM todavía no soltó el monitor fantasma que
        acabamos de apagar; sin esto se le reparten desktops a una pantalla que
        ya no existe.
        """
        monitors = self._window_manager_repo.list_monitors()
        if not connected:
            return monitors
        live = [monitor for monitor in monitors if monitor in connected]
        return live or monitors

    @staticmethod
    def _classify(names: list[str]) -> tuple[str | None, list[str]]:
        notebook = next((name for name in names if is_internal_output(name)), None)
        externals = [name for name in names if name != notebook]
        return notebook, externals

    @staticmethod
    def _order_by_side(
        notebook: str | None, externals: list[str], side: str
    ) -> list[str]:
        if notebook is None:
            return externals
        if side == "right":
            return [*externals, notebook]
        return [notebook, *externals]


# Backward compatibility while migrating call sites.
ApplyMonitorLayout = ApplyMonitorLayoutService
