"""Registro de hooks de instalación.

Los programas declarados en ``programs.json`` referencian estas funciones por nombre
en sus campos ``hooks.pre_install`` / ``hooks.post_install`` / ``hooks.post_uninstall``.
El loader (``ProgramLoaderRepository``) resuelve cada nombre contra ``HOOKS`` y arma las
tuplas ``pre/post_install_actions`` que espera ``ProgramConfig``.

Acá vive la única lógica imperativa que un programa necesita durante su instalación;
todo lo demás (paquetes, archivos, deps, tokens) es dato puro en el JSON.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.constants import path_config_files, path_dotfiles

logger = logging.getLogger(__name__)


# --- sxhkd -----------------------------------------------------------------
def sxhkd_reload() -> None:
    CommandRepository().run_argv_quiet(["pkill", "-USR1", "-x", "sxhkd"])


# --- vscode ----------------------------------------------------------------
_TOKEN_RE = re.compile(r"\{\{([a-zA-Z0-9_.]+)\}\}")


def _resolve_token(path: str, palette: dict[str, Any]) -> str:
    node: Any = palette
    for key in path.split("."):
        if isinstance(node, list):
            node = node[int(key)]
        elif isinstance(node, dict):
            if key not in node:
                raise KeyError(f"Token '{path}' not found in palette (missing '{key}')")
            node = node[key]
        else:
            raise KeyError(f"Token '{path}' not resolvable past '{key}'")
    if not isinstance(node, str):
        raise ValueError(
            f"Token '{path}' did not resolve to a string (got {type(node).__name__})"
        )
    return node


def vscode_render_settings() -> None:
    path_folder_vscode = path_config_files / "vscode"
    path_config_folder = path_folder_vscode / "_config"
    path_template = path_config_folder / "template_settings.jsonc"
    path_palette = path_config_folder / "config_aquamarine.json"
    path_output = path_folder_vscode / "settings.json"

    template = path_template.read_text(encoding="utf-8")
    palette = json.loads(path_palette.read_text(encoding="utf-8"))
    rendered = _TOKEN_RE.sub(lambda m: _resolve_token(m.group(1), palette), template)
    path_output.write_text(rendered, encoding="utf-8")


# --- fonts -----------------------------------------------------------------
def _list_font_files(source_dir: Path) -> list[Path]:
    if not source_dir.is_dir():
        return []
    patterns = ("*.ttf", "*.otf", "*.ttc")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(source_dir.glob(pattern))
    return sorted(files)


def _refresh_font_cache(destination_dir: Path) -> None:
    if shutil.which("fc-cache") is None:
        return
    subprocess.run(["fc-cache", "-f", str(destination_dir)], check=False)


def fonts_install_local() -> None:
    source_dir = path_dotfiles / "fonts"
    destination_dir = Path.home() / ".local" / "share" / "fonts"

    font_files = _list_font_files(source_dir)
    if not font_files:
        return

    destination_dir.mkdir(parents=True, exist_ok=True)
    for font_file in font_files:
        shutil.copy2(font_file, destination_dir / font_file.name)

    _refresh_font_cache(destination_dir)


# --- docker ----------------------------------------------------------------
def docker_enable_service() -> None:
    command_repo = CommandRepository()
    if not command_repo.command_exists("systemctl"):
        logger.warning("[docker] [post install skip] systemctl not found")
        return
    try:
        command_repo.run_argv(["sudo", "systemctl", "enable", "--now", "docker.service"])
    except subprocess.CalledProcessError:
        logger.info("[docker] [post install retry] falling back to enable + start")
        command_repo.run_argv(["sudo", "systemctl", "enable", "docker.service"])
        command_repo.run_argv(["sudo", "systemctl", "start", "docker.service"])


def docker_configure_group() -> None:
    command_repo = CommandRepository()
    if command_repo.run_argv_quiet(["getent", "group", "docker"]) != 0:
        command_repo.run_argv(["sudo", "groupadd", "docker"])

    user = os.environ.get("USER", "").strip()
    if not user:
        logger.warning("[docker] [post install skip] USER env var not available")
        return

    user_groups = command_repo.run_argv_capture(["id", "-nG", user]).split()
    if "docker" not in user_groups:
        command_repo.run_argv(["sudo", "usermod", "-aG", "docker", user])
        logger.info(
            "[docker] [post install] user added to docker group; relogin/reboot required"
        )


HOOKS: dict[str, Callable[[], None]] = {
    "sxhkd_reload": sxhkd_reload,
    "vscode_render_settings": vscode_render_settings,
    "fonts_install_local": fonts_install_local,
    "docker_enable_service": docker_enable_service,
    "docker_configure_group": docker_configure_group,
}
