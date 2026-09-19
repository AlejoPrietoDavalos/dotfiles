from __future__ import annotations

import logging
from abc import ABC
from typing import Sequence

from src.app.drivers.repositories.shell.command_repository import CommandRepository
from src.core.repositories.shell.command_repository import CoreCommandRepository
from src.core.repositories.pkg_manager.pkg_repository import CoreBasePkgRepository

logger = logging.getLogger(__name__)


class BasePkgRepository(CoreBasePkgRepository, ABC):
    def __init__(
        self,
        manager_name: str,
        install_cmd_prefix: Sequence[str],
        uninstall_cmd_prefix: Sequence[str],
        command_repo: CoreCommandRepository | None = None,
    ) -> None:
        self._manager_name = manager_name
        self._install_cmd_prefix = tuple(install_cmd_prefix)
        self._uninstall_cmd_prefix = tuple(uninstall_cmd_prefix)
        self._command_repo = command_repo or CommandRepository()

    @property
    def manager_name(self) -> str:
        return self._manager_name

    def _exists(self) -> bool:
        return self._command_repo.command_exists(self.manager_name)

    def _is_installed(self, pkg_name: str) -> bool:
        return self._command_repo.run_argv_quiet([self.manager_name, "-Q", pkg_name]) == 0

    def manager_exists(self) -> bool:
        return self._exists()

    def is_installed(self, pkg_names: list[str]) -> bool:
        return all(self._is_installed(pkg) for pkg in pkg_names)

    def _run_install(self, pkg_names: list[str]) -> None:
        self._command_repo.run_argv([*self._install_cmd_prefix, *pkg_names])

    def _run_uninstall(self, pkg_names: list[str]) -> None:
        self._command_repo.run_argv([*self._uninstall_cmd_prefix, *pkg_names])

    def install(self, pkg_names: list[str], program_name: str | None = None) -> None:
        program_tag = program_name or "unknown_program"
        if not self._exists():
            logger.warning("[%s] [requirements skip] manager '%s' not found", program_tag, self.manager_name)
            return
        if not pkg_names:
            logger.info("[%s] [requirements skip] empty package list", program_tag)
            return

        missing: list[str] = []
        for pkg in pkg_names:
            if self._is_installed(pkg):
                logger.info(
                    "[%s] [requirements skip] already installed: %s (%s)",
                    program_tag,
                    pkg,
                    self.manager_name,
                )
            else:
                missing.append(pkg)

        if not missing:
            return

        logger.info(
            "[%s] [requirements install] manager=%s packages=%s",
            program_tag,
            self.manager_name,
            ",".join(missing),
        )
        self._run_install(missing)

    def uninstall(self, pkg_names: list[str], program_name: str | None = None) -> None:
        program_tag = program_name or "unknown_program"
        if not self._exists():
            logger.warning("[%s] [requirements uninstall skip] manager '%s' not found", program_tag, self.manager_name)
            return
        if not pkg_names:
            logger.info("[%s] [requirements uninstall skip] empty package list", program_tag)
            return

        installed: list[str] = []
        for pkg in pkg_names:
            if self._is_installed(pkg):
                installed.append(pkg)
            else:
                logger.info(
                    "[%s] [requirements uninstall skip] not installed: %s (%s)",
                    program_tag,
                    pkg,
                    self.manager_name,
                )

        if not installed:
            return

        logger.info(
            "[%s] [requirements uninstall] manager=%s packages=%s",
            program_tag,
            self.manager_name,
            ",".join(installed),
        )
        self._run_uninstall(installed)
