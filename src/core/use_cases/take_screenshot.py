import shutil
import logging
from pathlib import Path
from typing import Literal

from src.core.constants import path_screenshots
from src.core.repositories.local_file import CoreTmpRepository
from src.core.repositories.system.clipboard_repository import CoreClipboardRepository
from src.core.repositories.system.screenshot_repository import CoreScreenshotRepository


CaptureMode = Literal["bbox", "focused", "full_screen"]
SaveMode = Literal[0, 1]

logger = logging.getLogger(__name__)


class TakeScreenshotService:
    def __init__(
        self,
        screenshot_repo: CoreScreenshotRepository,
        clipboard_repo: CoreClipboardRepository,
        tmp_repo: CoreTmpRepository,
        path_output_folder: Path = path_screenshots,
    ) -> None:
        self._screenshot_repo = screenshot_repo
        self._clipboard_repo = clipboard_repo
        self._tmp_repo = tmp_repo
        self._path_output_folder = path_output_folder

    def run(self, mode: CaptureMode, with_save: SaveMode) -> Path | None:
        logger.info("Screenshot started | mode=%s | with_save=%s", mode, with_save)
        try:
            with self._tmp_repo.temporary_png_path() as tmp_png:
                self._capture(mode, tmp_png)
                if not tmp_png.exists():
                    raise RuntimeError(f"Screenshot capture did not create output file: {tmp_png}")
                if tmp_png.stat().st_size == 0:
                    raise RuntimeError(f"Screenshot capture created an empty file: {tmp_png}")
                logger.info("Capture done: %s (%s bytes)", tmp_png, tmp_png.stat().st_size)
                self._clipboard_repo.copy_png_to_clipboard(tmp_png)
                logger.info("Image copied to clipboard")

                if with_save == 1:
                    path_output = self._next_screenshot_path()
                    shutil.move(str(tmp_png), str(path_output))
                    logger.info("Screenshot saved: %s", path_output)
                    return path_output
                logger.info("Screenshot completed without file save")
                return None
        except Exception:
            logger.exception("Screenshot flow failed")
            raise

    def _capture(self, mode: CaptureMode, path_output_png: Path) -> None:
        if mode == "bbox":
            self._screenshot_repo.capture_bbox(path_output_png)
            return
        if mode == "focused":
            self._screenshot_repo.capture_focused(path_output_png)
            return
        self._screenshot_repo.capture_full_screen(path_output_png)

    def _next_screenshot_path(self) -> Path:
        self._path_output_folder.mkdir(parents=True, exist_ok=True)
        current_indexes = [
            int(path_png.stem)
            for path_png in self._path_output_folder.glob("*.png")
            if path_png.stem.isdigit()
        ]
        next_index = (max(current_indexes) + 1) if current_indexes else 1
        return self._path_output_folder / f"{next_index}.png"
