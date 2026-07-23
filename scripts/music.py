#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import cast

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app.drivers.repositories.system.media_player_repository import (
    PlayerctlMediaPlayerRepository,
)
from src.app.drivers.repositories.logs import ConfigureLoggingRepository
from src.core.repositories.system.media_player_repository import (
    MediaPlayerAction,
)

def main(action: MediaPlayerAction) -> int:
    configure_logging_repo = ConfigureLoggingRepository()
    configure_logging_repo.configure(log_filename=f"{Path(__file__).stem}.log")
    repo = PlayerctlMediaPlayerRepository()
    repo.run(action)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["previous", "next", "play_pause", "stop"])
    args = parser.parse_args()
    raise SystemExit(main(cast(MediaPlayerAction, args.action)))
