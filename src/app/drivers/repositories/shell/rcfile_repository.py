import hashlib
from pathlib import Path

from src.core.constants import path_cache
from src.core.repositories.shell.rcfile_repository import CoreShellRcfileRepository


class BashRcfileRepository(CoreShellRcfileRepository):
    """Rcfile de bash que sourcea ``~/.bashrc`` y después el venv.

    Hace falta porque ``bash --rcfile`` reemplaza al ``~/.bashrc`` en vez de
    sumarse: sin componer los dos, activar el venv te deja sin la config de la
    shell. El nombre sale del hash del activate, así que es estable por venv y
    se reescribe idempotentemente.
    """

    def __init__(self, cache_dir: Path | None = None) -> None:
        self._cache_dir = cache_dir or path_cache / "rcfiles"

    def rcfile_for(self, activate_script: Path) -> Path:
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(str(activate_script).encode()).hexdigest()[:12]
        rcfile = self._cache_dir / f"rc_{digest}.bash"
        rcfile.write_text(
            "# Generado por `dot`: no editar, se reescribe solo.\n"
            '[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"\n'
            f'. "{activate_script}"\n',
            encoding="utf-8",
        )
        return rcfile
