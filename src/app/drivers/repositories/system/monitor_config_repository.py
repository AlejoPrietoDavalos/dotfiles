import json
import logging
from pathlib import Path

from src.core.constants import path_dotfiles
from src.core.entities.monitor_layout import MonitorLayoutConfig
from src.core.repositories.system.monitor_config_repository import (
    CoreMonitorConfigRepository,
)

logger = logging.getLogger(__name__)

# La elección es física y depende de la máquina (de qué lado está la notebook),
# por eso vive en ~/.config y NO se versiona en el repo.
DEFAULT_CONFIG_PATH = path_dotfiles / "bspwm" / "monitors.json"


class JsonMonitorConfigRepository(CoreMonitorConfigRepository):
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or DEFAULT_CONFIG_PATH

    def load(self) -> MonitorLayoutConfig:
        if not self._path.is_file():
            return MonitorLayoutConfig()
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return MonitorLayoutConfig.from_dict(data)
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            logger.warning(
                "[monitors] config inválida en %s (%s); uso valores por defecto",
                self._path,
                exc,
            )
            return MonitorLayoutConfig()

    def save(self, config: MonitorLayoutConfig) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(config.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
