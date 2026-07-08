from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal, get_args

PkgManager = Literal["pacman", "yay"]
FileMode = Literal["link", "copy"]
ProgramName = Literal[
    "fonts",
    "bspwm",
    "sxhkd",
    "polybar",
    "kitty",
    "starship",
    "ranger",
    "picom",
    "rofi",
    "playerctl",
    "scrot",
    "thunar",
    "vscode",
    "xclip",
    "pulseaudio",
    "arandr",
    "xorg",
    "nvidia",
    "docker",
]
PROGRAM_NAMES: tuple[ProgramName, ...] = get_args(ProgramName)
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
        if self.name not in PROGRAM_NAMES:
            raise ValueError(f"Invalid program '{self.name}'. Available: {PROGRAM_NAMES}")
        for dep in self.program_dependencies:
            if dep not in PROGRAM_NAMES:
                raise ValueError(
                    f"Invalid dependency '{dep}' in program '{self.name}'. "
                    f"Available: {PROGRAM_NAMES}"
                )
