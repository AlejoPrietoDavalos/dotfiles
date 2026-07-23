from src.app.drivers.repositories.pkg_manager._implementations.base_pkg_repository import BasePkgRepository


class AptPkgRepository(BasePkgRepository):
    """Package manager de Debian/Ubuntu.

    A diferencia de pacman/yay (`-Q`), el chequeo de instalado usa `dpkg -s`,
    que devuelve exit 0 si el paquete está instalado.
    """

    def __init__(self) -> None:
        super().__init__(
            manager_name="apt",
            install_cmd_prefix=["sudo", "apt-get", "install", "-y"],
            uninstall_cmd_prefix=["sudo", "apt-get", "remove", "-y"],
        )

    def _is_installed(self, pkg_name: str) -> bool:
        return self._command_repo.run_argv_quiet(["dpkg", "-s", pkg_name]) == 0
