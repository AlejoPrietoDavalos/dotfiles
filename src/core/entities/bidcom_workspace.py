"""Dominio del workspace de trabajo (Bidcom): qué abrir y dónde.

La config real vive en ``private/bidcom.json`` (gitignoreado: nombres de repos
y layout de trabajo no se versionan). Este módulo define las entidades y los
valores por defecto; el primer ``dot bidcom start-work`` materializa el JSON.

Los desktops aceptan tanto el nombre bspwm (``n1``-``n4``, ``1``-``0``) como el
símbolo del pad numérico (``/ * - +``) que muestra polybar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.core.entities.monitor_layout import DESKTOPS, PAD_DESKTOPS

# Símbolos del pad (como los muestra polybar) -> nombre real del desktop bspwm.
PAD_ALIASES: dict[str, str] = {"/": "n1", "*": "n2", "-": "n3", "+": "n4"}

VALID_DESKTOPS: set[str] = {*DESKTOPS, *PAD_DESKTOPS}


def normalize_desktop(name: str) -> str:
    """Lleva ``/ * - +`` a ``n1``-``n4`` y valida que el desktop exista."""
    desktop = PAD_ALIASES.get(name.strip(), name.strip())
    if desktop not in VALID_DESKTOPS:
        raise ValueError(
            f"Desktop inválido '{name}'. Válidos: {sorted(VALID_DESKTOPS)} "
            f"o alias del pad {list(PAD_ALIASES)}"
        )
    return desktop


@dataclass(frozen=True)
class VscodeWorkspace:
    """Un repo a abrir con VSCode en un desktop concreto."""

    repo: str
    desktop: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "desktop", normalize_desktop(self.desktop))


@dataclass(frozen=True)
class TerminalSpec:
    """N terminales en un repo/desktop, con o sin venv (``<repo>/env``)."""

    repo: str
    desktop: str
    count: int = 1
    venv: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "desktop", normalize_desktop(self.desktop))
        if self.count < 1:
            raise ValueError(f"count debe ser >= 1 (repo {self.repo})")


@dataclass(frozen=True)
class AppSpec:
    """Aplicación a dejar corriendo en un desktop (docker-desktop, slack...).

    - ``systemd_user_unit``: si se define, se levanta con ``systemctl --user``.
    - ``command``: si se define, se lanza como proceso suelto.
    - ``process``: nombre para chequear con pgrep si ya está corriendo.
    """

    name: str
    desktop: str
    wm_class: str
    command: list[str] | None = None
    systemd_user_unit: str | None = None
    process: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "desktop", normalize_desktop(self.desktop))
        if not self.command and not self.systemd_user_unit:
            raise ValueError(f"App '{self.name}': falta command o systemd_user_unit")


@dataclass(frozen=True)
class BidcomWorkspaceConfig:
    workspaces_root: Path = Path.home() / "documentos" / "python"
    venv_dirname: str = "env"
    terminal_program: str = "kitty"  # el mismo que sxhkd (super+Enter)
    terminal_wm_class: str = "kitty"
    # bspwm matchea WM_CLASS case-sensitive; VSCode acá reporta "code","code".
    vscode_wm_class: str = "code"
    final_focus_desktop: str | None = "1"
    vscode: tuple[VscodeWorkspace, ...] = field(default_factory=tuple)
    terminals: tuple[TerminalSpec, ...] = field(default_factory=tuple)
    apps: tuple[AppSpec, ...] = field(default_factory=tuple)

    def repo_path(self, repo: str) -> Path:
        return self.workspaces_root / repo

    # ------------------------------------------------------------- (de)serialización
    def to_dict(self) -> dict:
        return {
            "workspaces_root": str(self.workspaces_root),
            "venv_dirname": self.venv_dirname,
            "terminal": {
                "program": self.terminal_program,
                "wm_class": self.terminal_wm_class,
            },
            "vscode": {
                "wm_class": self.vscode_wm_class,
                "workspaces": [
                    {"repo": ws.repo, "desktop": ws.desktop} for ws in self.vscode
                ],
            },
            "terminals": [
                {
                    "repo": term.repo,
                    "desktop": term.desktop,
                    "count": term.count,
                    "venv": term.venv,
                }
                for term in self.terminals
            ],
            "apps": [
                {
                    "name": app.name,
                    "desktop": app.desktop,
                    "wm_class": app.wm_class,
                    **({"command": app.command} if app.command else {}),
                    **(
                        {"systemd_user_unit": app.systemd_user_unit}
                        if app.systemd_user_unit
                        else {}
                    ),
                    **({"process": app.process} if app.process else {}),
                }
                for app in self.apps
            ],
            "final_focus_desktop": self.final_focus_desktop,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BidcomWorkspaceConfig":
        defaults = cls()
        terminal = data.get("terminal", {})
        vscode = data.get("vscode", {})
        return cls(
            workspaces_root=Path(
                data.get("workspaces_root", defaults.workspaces_root)
            ).expanduser(),
            venv_dirname=data.get("venv_dirname", defaults.venv_dirname),
            terminal_program=terminal.get("program", defaults.terminal_program),
            terminal_wm_class=terminal.get("wm_class", defaults.terminal_wm_class),
            vscode_wm_class=vscode.get("wm_class", defaults.vscode_wm_class),
            final_focus_desktop=data.get(
                "final_focus_desktop", defaults.final_focus_desktop
            ),
            vscode=tuple(
                VscodeWorkspace(repo=ws["repo"], desktop=str(ws["desktop"]))
                for ws in vscode.get("workspaces", [])
            ),
            terminals=tuple(
                TerminalSpec(
                    repo=term["repo"],
                    desktop=str(term["desktop"]),
                    count=int(term.get("count", 1)),
                    venv=bool(term.get("venv", True)),
                )
                for term in data.get("terminals", [])
            ),
            apps=tuple(
                AppSpec(
                    name=app["name"],
                    desktop=str(app["desktop"]),
                    wm_class=app["wm_class"],
                    command=app.get("command"),
                    systemd_user_unit=app.get("systemd_user_unit"),
                    process=app.get("process"),
                )
                for app in data.get("apps", [])
            ),
        )

    @classmethod
    def default(cls) -> "BidcomWorkspaceConfig":
        """Plantilla de ejemplo: VSCode en 1-2, terminales en el pad, apps en 9.

        Es solo el esqueleto que se escribe la primera vez en `private/bidcom.json`
        para editar a mano; los repos reales viven ahi y no se versionan.
        """
        return cls(
            vscode=(
                VscodeWorkspace("repo-a", "1"),
                VscodeWorkspace("repo-b", "2"),
            ),
            terminals=(
                TerminalSpec("repo-a", "/"),
                TerminalSpec("repo-b", "*", count=2),
            ),
            apps=(
                AppSpec(
                    name="docker-desktop",
                    desktop="9",
                    wm_class="Docker Desktop",
                    systemd_user_unit="docker-desktop.service",
                    process="Docker Desktop",
                ),
                AppSpec(
                    name="slack",
                    desktop="9",
                    wm_class="slack",
                    command=["slack"],
                    process="slack",
                ),
            ),
        )
