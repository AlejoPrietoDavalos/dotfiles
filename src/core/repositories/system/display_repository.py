from abc import ABC, abstractmethod


class CoreDisplayRepository(ABC):
    @abstractmethod
    def list_connected_outputs(self) -> list[str]:
        ...

    @abstractmethod
    def list_active_outputs(self) -> list[str]:
        ...

    @abstractmethod
    def enable_outputs_auto(self, outputs: list[str]) -> None:
        ...
