from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal, get_args

PkgManager = Literal["pacman", "yay"]
FileMode = Literal["link", "copy"]

# Los nombres de programa ya no son un Literal fijo: la lista válida la define
# ``programs.json`` en runtime (ver ProgramLoaderRepository). Un nombre es cualquier
# string no vacío; el loader falla claro si se pide uno que no existe en el JSON.
ProgramName = str

PKG_MANAGERS: tuple[PkgManager, ...] = get_args(PkgManager)
FILE_MODES: tuple[FileMode, ...] = get_args(FileMode)


@dataclass(frozen=True)
class PkgSpec:
    manager: PkgManager
    names: list[str]

    def __post_init__(self) -> None:
        if self.manager not in PKG_MANAGERS:
            raise ValueError(
                f"Invalid package manager '{self.manager}'. Available: {PKG_MANAGERS}"
            )


@dataclass(frozen=True)
class Packages:
    pkg_specs: list[PkgSpec]


@dataclass(frozen=True)
class ProgramFiles:
    path_folder_config_files_input: Path
    path_folder_program_dotfile: Path
    mode: FileMode = "copy"

    """Tokens específicos del programa para reemplazar en sus archivos de configuración. Formato: {"{{NOMBRE}}": "valor"}."""
    extra_tokens: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.mode not in FILE_MODES:
            raise ValueError(f"Invalid files mode '{self.mode}'. Available: {FILE_MODES}")


@dataclass(frozen=True)
class ProgramConfig:
    name: ProgramName
    package_dependencies: Packages
    files: ProgramFiles | None = None
    program_dependencies: tuple[ProgramName, ...] = field(default_factory=tuple)
    pre_install_actions: tuple[Callable[[], None], ...] = field(default_factory=tuple)
    post_install_actions: tuple[Callable[[], None], ...] = field(default_factory=tuple)
    post_uninstall_actions: tuple[Callable[[], None], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("ProgramConfig.name must be a non-empty string")
        # La validación de que 'name' y cada dep existan como programa la hace el loader
        # (ProgramLoaderRepository) contra las claves de programs.json.
