from src.core.constants import path_config_files, path_dotfiles
from src.core.entities.program_config import PkgSpec, Packages
from src.core.entities.program_config import ProgramConfig, ProgramFiles
from src.core.repositories.programs._implementations.starship_repository import CoreStarshipRepository


class StarshipRepository(CoreStarshipRepository):
    def default_config(self) -> ProgramConfig:
        return ProgramConfig(
            name="starship",
            files=ProgramFiles(
                # La carpeta contiene starship.toml; se copia a ~/.config/starship.toml.
                path_folder_config_files_input=path_config_files / "starship",
                path_folder_program_dotfile=path_dotfiles,
            ),
            package_dependencies=Packages(pkg_specs=[PkgSpec(manager="pacman", names=["starship"])]),
        )
