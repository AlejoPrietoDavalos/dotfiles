from abc import ABC, abstractmethod
from pathlib import Path


class CoreScreenshotRepository(ABC):
    @abstractmethod
    def capture_bbox(self, path_output_png: Path) -> None:
        ...

    @abstractmethod
    def capture_focused(self, path_output_png: Path) -> None:
        ...

    @abstractmethod
    def capture_full_screen(self, path_output_png: Path) -> None:
        ...
