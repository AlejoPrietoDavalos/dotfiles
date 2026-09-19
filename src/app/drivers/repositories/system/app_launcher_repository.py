import subprocess
from pathlib import Path

from src.core.repositories.system.app_launcher_repository import (
    CoreAppLauncherRepository,
)


class LinuxAppLauncherRepository(CoreAppLauncherRepository):
    def launch_detached(self, argv: list[str], cwd: Path | None = None) -> None:
        subprocess.Popen(
            argv,
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    def is_process_running(self, name: str) -> bool:
        # -f: matchea contra la línea de comando completa (cubre procesos tipo
        # "Docker Desktop" cuyo comm real es otro binario).
        return (
            subprocess.run(
                ["pgrep", "-f", name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )

    def is_user_service_active(self, unit: str) -> bool:
        return (
            subprocess.run(
                ["systemctl", "--user", "is-active", "--quiet", unit],
                check=False,
            ).returncode
            == 0
        )

    def start_user_service(self, unit: str) -> None:
        subprocess.run(["systemctl", "--user", "start", unit], check=True)
