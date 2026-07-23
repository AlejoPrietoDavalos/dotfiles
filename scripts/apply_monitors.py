#!/usr/bin/env python3
"""Apply monitor layout for bspwm using the core use case."""

from src.app.drivers.repositories.logs import ConfigureLoggingRepository
from src.app.drivers.repositories.system.display_repository import (
    XrandrDisplayRepository,
)
from src.app.drivers.repositories.system.window_manager_repository import (
    BspwmWindowManagerRepository,
)
from src.core.use_cases.apply_monitor_layout import ApplyMonitorLayoutService

REVERSE_MONITOR_LAYOUT = False


def main() -> int:
    configure_logging_repo = ConfigureLoggingRepository()
    configure_logging_repo.configure(log_filename="apply_monitors.log")
    use_case = ApplyMonitorLayoutService(
        display_repo=XrandrDisplayRepository(),
        window_manager_repo=BspwmWindowManagerRepository(),
        reverse_monitor_layout=REVERSE_MONITOR_LAYOUT,
    )
    use_case.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
