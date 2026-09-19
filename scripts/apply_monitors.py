#!/usr/bin/env python3
"""Aplica la distribución guardada de monitores/desktops para bspwm.

Lo llama ``bspwmrc`` al arrancar. La elección (lado de la notebook + reparto)
se guarda con ``dot monitors``; acá sólo se lee y se aplica.
"""

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
from src.core.use_cases.apply_monitor_layout import ApplyMonitorLayoutService


def main() -> int:
    configure_logging_repo = ConfigureLoggingRepository()
    configure_logging_repo.configure(log_filename="apply_monitors.log")
    use_case = ApplyMonitorLayoutService(
        display_repo=XrandrDisplayRepository(),
        window_manager_repo=BspwmWindowManagerRepository(),
        config_repo=JsonMonitorConfigRepository(),
    )
    use_case.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
