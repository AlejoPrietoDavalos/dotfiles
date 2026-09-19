"""Arranque del día de trabajo: VSCode por desktop, terminales con venv y apps.

El problema fino acá es la carrera con el WM: si lanzás una app y cambiás de
desktop antes de que mapee su ventana, la ventana nace donde no era. Se ataca
por dos lados:

1. Regla one-shot del WM (``bspc rule -o``): la próxima ventana de esa clase
   nace directo en el desktop pedido, sin depender del foco.
2. Verificación: se espera a que la ventana nueva aparezca de verdad y, si aun
   así quedó en otro desktop, se la mueve. Recién ahí se lanza la siguiente.
"""

from __future__ import annotations

import logging
import time
from typing import Callable, Iterable

from src.core.entities.bidcom_workspace import AppSpec, BidcomWorkspaceConfig
from src.core.repositories.system.app_launcher_repository import (
    CoreAppLauncherRepository,
)
from src.core.repositories.system.terminal_repository import CoreTerminalRepository
from src.core.repositories.system.window_manager_repository import (
    CoreWindowManagerRepository,
)

logger = logging.getLogger(__name__)

SECTIONS = ("vscode", "terminals", "apps")

_POLL_SECONDS = 0.25
_VSCODE_TIMEOUT = 40.0
_TERMINAL_TIMEOUT = 10.0
_APP_TIMEOUT = 45.0


class BidcomStartWorkService:
    def __init__(
        self,
        config: BidcomWorkspaceConfig,
        window_manager_repo: CoreWindowManagerRepository,
        launcher_repo: CoreAppLauncherRepository,
        terminal_repo: CoreTerminalRepository,
    ) -> None:
        self._config = config
        self._wm = window_manager_repo
        self._launcher = launcher_repo
        self._terminal = terminal_repo

    def run(self, sections: Iterable[str] | None = None) -> None:
        wanted = set(sections or SECTIONS)
        self._desktops = set(self._wm.list_desktops())
        if not self._desktops:
            raise SystemExit("bspwm no responde (¿bspc en PATH y sesión corriendo?).")
        if "vscode" in wanted:
            self._open_vscode_workspaces()
        if "terminals" in wanted:
            self._open_terminals()
        if "apps" in wanted:
            self._launch_apps()
        self._focus_final_desktop()

    # ------------------------------------------------------------------ vscode
    def _open_vscode_workspaces(self) -> None:
        for workspace in self._config.vscode:
            path = self._config.repo_path(workspace.repo)
            if not path.is_dir():
                logger.warning("[vscode] repo inexistente, salteo: %s", path)
                continue
            if not self._desktop_available(workspace.desktop, f"vscode {workspace.repo}"):
                continue
            logger.info("[vscode] %s -> desktop %s", workspace.repo, workspace.desktop)
            self._launch_and_place(
                wm_class=self._config.vscode_wm_class,
                desktop=workspace.desktop,
                launch=lambda p=path: self._launcher.launch_detached(["code", str(p)]),
                timeout=_VSCODE_TIMEOUT,
                label=f"vscode {workspace.repo}",
            )

    # --------------------------------------------------------------- terminales
    def _open_terminals(self) -> None:
        for spec in self._config.terminals:
            path = self._config.repo_path(spec.repo)
            if not path.is_dir():
                logger.warning("[terminal] repo inexistente, salteo: %s", path)
                continue
            if not self._desktop_available(spec.desktop, f"terminal {spec.repo}"):
                continue
            activate = None
            if spec.venv:
                candidate = path / self._config.venv_dirname / "bin" / "activate"
                if candidate.is_file():
                    activate = candidate
                else:
                    logger.warning(
                        "[terminal] %s sin venv (%s no existe); abro sin activar",
                        spec.repo,
                        candidate,
                    )
            for index in range(spec.count):
                logger.info(
                    "[terminal] %s -> desktop %s (%d/%d)%s",
                    spec.repo,
                    spec.desktop,
                    index + 1,
                    spec.count,
                    " + venv" if activate else "",
                )
                self._launch_and_place(
                    wm_class=self._config.terminal_wm_class,
                    desktop=spec.desktop,
                    launch=lambda a=activate: self._terminal.open(path, a),
                    timeout=_TERMINAL_TIMEOUT,
                    label=f"terminal {spec.repo}",
                )

    # -------------------------------------------------------------------- apps
    def _launch_apps(self) -> None:
        for app in self._config.apps:
            if not self._desktop_available(app.desktop, f"app {app.name}"):
                continue
            if self._app_already_running(app):
                logger.info("[apps] %s ya está corriendo", app.name)
                self._relocate_existing_window(app)
                continue
            logger.info("[apps] lanzo %s -> desktop %s", app.name, app.desktop)
            self._launch_and_place(
                wm_class=app.wm_class,
                desktop=app.desktop,
                launch=lambda a=app: self._start_app(a),
                timeout=_APP_TIMEOUT,
                label=f"app {app.name}",
            )

    def _app_already_running(self, app: AppSpec) -> bool:
        if app.systemd_user_unit and self._launcher.is_user_service_active(
            app.systemd_user_unit
        ):
            return True
        return bool(app.process) and self._launcher.is_process_running(app.process)

    def _start_app(self, app: AppSpec) -> None:
        if app.systemd_user_unit:
            self._launcher.start_user_service(app.systemd_user_unit)
        elif app.command:
            self._launcher.launch_detached(list(app.command))

    def _relocate_existing_window(self, app: AppSpec) -> None:
        """Si la app ya corre pero su ventana quedó en otro desktop, la acomoda."""
        for window_id in self._wm.list_window_ids():
            if not self._class_matches(window_id, app.wm_class):
                continue
            current = self._wm.desktop_of_window(window_id)
            if current and current != app.desktop:
                logger.info(
                    "[apps] muevo ventana de %s: %s -> %s",
                    app.name,
                    current,
                    app.desktop,
                )
                self._wm.move_window_to_desktop(window_id, app.desktop)

    # ----------------------------------------------------------------- helpers
    def _launch_and_place(
        self,
        wm_class: str,
        desktop: str,
        launch: Callable[[], None],
        timeout: float,
        label: str,
    ) -> None:
        known = set(self._wm.list_window_ids())
        self._wm.add_one_shot_rule(wm_class, desktop)
        launch()
        window_id = self._wait_new_window(known, wm_class, timeout)
        if window_id is None:
            # Sin ventana nueva la one-shot quedó pendiente: si no se borra,
            # desviaría la próxima ventana de esta clase que abra el usuario.
            self._wm.remove_rules(wm_class)
            logger.warning(
                "[%s] no apareció ventana nueva de clase '%s' en %.0fs "
                "(¿ya estaba abierta?)",
                label,
                wm_class,
                timeout,
            )
            return
        actual = self._wm.desktop_of_window(window_id)
        if actual != desktop:
            logger.info("[%s] nació en '%s'; la muevo a '%s'", label, actual, desktop)
            self._wm.move_window_to_desktop(window_id, desktop)

    def _wait_new_window(
        self, known: set[str], wm_class: str, timeout: float
    ) -> str | None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for window_id in set(self._wm.list_window_ids()) - known:
                if self._class_matches(window_id, wm_class):
                    return window_id
            time.sleep(_POLL_SECONDS)
        return None

    def _class_matches(self, window_id: str, wm_class: str) -> bool:
        tokens = [token.lower() for token in self._wm.window_class(window_id)]
        return wm_class.lower() in tokens

    def _desktop_available(self, desktop: str, label: str) -> bool:
        if desktop in self._desktops:
            return True
        logger.warning(
            "[%s] desktop '%s' no existe en bspwm; salteo. "
            "(¿distribución 'pad' aplicada? probá `dot monitors`)",
            label,
            desktop,
        )
        return False

    def _focus_final_desktop(self) -> None:
        final = self._config.final_focus_desktop
        if final and final in self._desktops:
            self._wm.focus_desktop(final)
