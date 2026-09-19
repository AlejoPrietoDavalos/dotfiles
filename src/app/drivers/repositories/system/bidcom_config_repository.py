import json
import logging
from pathlib import Path

from src.core.constants import path_private
from src.core.entities.bidcom_workspace import BidcomWorkspaceConfig
from src.core.repositories.system.bidcom_config_repository import (
    CoreBidcomConfigRepository,
)

logger = logging.getLogger(__name__)

# Nombres de repos internos y layout de trabajo: NO se versiona (private/ está
# en .gitignore). El primer `dot bidcom start-work` lo crea con los defaults.
DEFAULT_CONFIG_PATH = path_private / "bidcom.json"


class JsonBidcomConfigRepository(CoreBidcomConfigRepository):
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or DEFAULT_CONFIG_PATH

    def load(self) -> BidcomWorkspaceConfig:
        if not self._path.is_file():
            return BidcomWorkspaceConfig.default()
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return BidcomWorkspaceConfig.from_dict(data)
        except (json.JSONDecodeError, ValueError, KeyError, OSError) as exc:
            raise SystemExit(f"Config inválida en {self._path}: {exc}")

    def save(self, config: BidcomWorkspaceConfig) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(config.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def location(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.is_file()
