from src.app.drivers.repositories.pkg_manager import PacmanPkgRepository, YayPkgRepository, AptPkgRepository
from src.core.entities.program_config import PkgManager, Packages
from src.core.repositories.pkg_manager.pkg_repository import CoreBasePkgRepository
from src.core.repositories.pkg_manager.factory_repository import CorePkgManagerFactoryRepository


def _get_available_pkg_managers() -> tuple[CoreBasePkgRepository, ...]:
    return (
        PacmanPkgRepository(),
        YayPkgRepository(),
        AptPkgRepository(),
    )


class PkgManagerFactoryRepository(CorePkgManagerFactoryRepository):
    def __init__(self) -> None:
        self._pkg_repos: dict[str, CoreBasePkgRepository] = {
            repo.manager_name: repo for repo in _get_available_pkg_managers()
        }

    def _manager2repo(self, manager: PkgManager) -> CoreBasePkgRepository:
        return self._pkg_repos[manager]

    def install(self, pkgs: Packages, program_name: str | None = None) -> None:
        for pkg_spec in pkgs.pkg_specs:
            repo = self._manager2repo(pkg_spec.manager)
            repo.install(pkg_spec.names, program_name=program_name)

    def uninstall(self, pkgs: Packages, program_name: str | None = None) -> None:
        for pkg_spec in pkgs.pkg_specs:
            repo = self._manager2repo(pkg_spec.manager)
            repo.uninstall(pkg_spec.names, program_name=program_name)
