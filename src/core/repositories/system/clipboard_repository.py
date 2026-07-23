from abc import ABC, abstractmethod
from pathlib import Path


class CoreClipboardRepository(ABC):
    @abstractmethod
    def copy_png_to_clipboard(self, path_png: Path) -> None:
        ...
