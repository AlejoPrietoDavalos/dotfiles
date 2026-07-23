from abc import ABC, abstractmethod

from src.core.entities.program_config import ProgramConfig, ProgramName


class CoreProgramLoaderRepository(ABC):
    """Puerto que provee los ProgramConfig declarados en programs.json.

    Reemplaza al viejo factory de clases por-programa: en vez de instanciar una clase
    por programa, se lee el dato del JSON y se construye el ProgramConfig.
    """

    @abstractmethod
    def get_config(self, program: ProgramName) -> ProgramConfig:
        ...

    @abstractmethod
    def list_programs(self) -> list[ProgramName]:
        ...
