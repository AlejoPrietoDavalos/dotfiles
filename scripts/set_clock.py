#!/usr/bin/env python3
"""Set timezone and sync hardware clock."""

import argparse

from src.app.drivers.repositories.logs import ConfigureLoggingRepository
from src.app.drivers.repositories.system.clock_repository import (
    HwclockClockRepository,
)


def main() -> int:
    configure_logging_repo = ConfigureLoggingRepository()
    configure_logging_repo.configure(log_filename="set_clock.log")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--timezone",
        default="America/Argentina/Buenos_Aires",
        help="Timezone path under /usr/share/zoneinfo",
    )
    args = parser.parse_args()

    repo = HwclockClockRepository()
    repo.set_timezone(args.timezone)
    repo.sync_system_to_hardware()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
