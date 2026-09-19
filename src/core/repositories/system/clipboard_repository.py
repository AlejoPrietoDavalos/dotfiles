from abc import ABC, abstractmethod
from pathlib import Path

# El portapapeles de X no guarda "texto": guarda el MISMO contenido en varios formatos
# (targets) a la vez, y quien lee elige cuál quiere. Una captura de pantalla ofrece solo
# `image/png` y NINGUNA representación de texto — por eso pedirle texto devuelve vacío.
IMAGE_TARGET = "image/png"


class CoreClipboardRepository(ABC):
    @abstractmethod
    def copy_png_to_clipboard(self, path_png: Path) -> None: ...

    @abstractmethod
    def targets(self) -> list[str]:
        """Los formatos que ofrece el portapapeles ahora mismo."""
        ...

    @abstractmethod
    def read_text(self) -> str:
        """El contenido como texto. Vacío si el portapapeles no ofrece texto."""
        ...

    @abstractmethod
    def write_text(self, text: str) -> None: ...

    @abstractmethod
    def save_png_to(self, path_png: Path) -> bool:
        """Vuelca la imagen del portapapeles a un archivo. False si no hay imagen."""
        ...
