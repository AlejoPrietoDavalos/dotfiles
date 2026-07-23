from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from src.app.drivers.repositories.programs.hooks import HOOKS
from src.core.constants import path_config_files, path_repo
from src.core.entities.program_config import (
    Packages,
    PkgSpec,
    ProgramConfig,
    ProgramFiles,
    ProgramName,
)
from src.core.repositories.programs.program_loader_repository import (
    CoreProgramLoaderRepository,
)

_PROGRAMS_JSON = path_repo / "programs.json"


def _expand_dst(dst: str) -> Path:
    """Expande '~' a la home del usuario. El resto de la ruta se toma literal."""
    return Path(dst).expanduser()


def _wrap_tokens(tokens: dict[str, str]) -> dict[str, str]:
    """Envuelve cada clave en '{{...}}', el formato que espera el template renderer."""
    return {f"{{{{{key}}}}}": value for key, value in tokens.items()}


def _resolve_hooks(names: list[str], program: str, slot: str) -> tuple[Callable[[], None], ...]:
    resolved: list[Callable[[], None]] = []
    for name in names:
        if name not in HOOKS:
            raise ValueError(
                f"Program '{program}' references unknown {slot} hook '{name}'. "
                f"Available hooks: {sorted(HOOKS)}"
            )
        resolved.append(HOOKS[name])
    return tuple(resolved)


def _build_config(name: str, raw: dict[str, Any]) -> ProgramConfig:
    packages = Packages(
        pkg_specs=[
            PkgSpec(manager=spec["manager"], names=list(spec["names"]))
            for spec in raw["packages"]
        ]
    )

    files = None
    raw_files = raw.get("files")
    if raw_files is not None:
        files = ProgramFiles(
            path_folder_config_files_input=path_config_files / raw_files["src"],
            path_folder_program_dotfile=_expand_dst(raw_files["dst"]),
            mode=raw_files.get("mode", "copy"),
            extra_tokens=_wrap_tokens(raw_files.get("tokens", {})),
        )

    hooks = raw.get("hooks", {})
    return ProgramConfig(
        name=name,
        package_dependencies=packages,
        files=files,
        program_dependencies=tuple(raw.get("deps", [])),
        pre_install_actions=_resolve_hooks(hooks.get("pre_install", []), name, "pre_install"),
        post_install_actions=_resolve_hooks(hooks.get("post_install", []), name, "post_install"),
        post_uninstall_actions=_resolve_hooks(
            hooks.get("post_uninstall", []), name, "post_uninstall"
        ),
    )


class ProgramLoaderRepository(CoreProgramLoaderRepository):
    def __init__(self, path_json: Path = _PROGRAMS_JSON) -> None:
        raw = json.loads(path_json.read_text(encoding="utf-8"))
        self._configs: dict[ProgramName, ProgramConfig] = {
            name: _build_config(name, cfg) for name, cfg in raw.items()
        }
        self._validate_deps()

    def _validate_deps(self) -> None:
        known = set(self._configs)
        for name, cfg in self._configs.items():
            for dep in cfg.program_dependencies:
                if dep not in known:
                    raise ValueError(
                        f"Program '{name}' depends on unknown program '{dep}'. "
                        f"Available: {sorted(known)}"
                    )

    def get_config(self, program: ProgramName) -> ProgramConfig:
        if program not in self._configs:
            raise ValueError(
                f"Unknown program '{program}'. Available: {sorted(self._configs)}"
            )
        cfg = self._configs[program]
        if cfg.files is not None and not cfg.files.path_folder_config_files_input.is_dir():
            raise ValueError(
                f"Missing files dir for '{program}': "
                f"{cfg.files.path_folder_config_files_input}"
            )
        return cfg

    def list_programs(self) -> list[ProgramName]:
        return list(self._configs.keys())
