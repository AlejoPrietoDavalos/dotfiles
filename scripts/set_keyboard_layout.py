#!/usr/bin/env python3
"""Set keyboard layout with setxkbmap."""

import argparse

from src.app.drivers.repositories.logs import ConfigureLoggingRepository
from src.app.drivers.repositories.system.keyboard_repository import (
    SetxkbmapKeyboardRepository,
)


def main() -> int:
    configure_logging_repo = ConfigureLoggingRepository()
    configure_logging_repo.configure(log_filename="set_keyboard_layout.log")
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", default="latam")
    args = parser.parse_args()

    repo = SetxkbmapKeyboardRepository()
    repo.set_layout(args.layout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
