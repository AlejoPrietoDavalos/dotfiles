from abc import ABC, abstractmethod


class CoreDisplayRepository(ABC):
    @abstractmethod
    def list_connected_outputs(self) -> list[str]:
        ...

    @abstractmethod
    def list_active_outputs(self) -> list[str]:
        ...

    @abstractmethod
    def list_stale_outputs(self) -> list[str]:
        """Outputs desconectados que xrandr todavía tiene encendidos.

        Pasa al desenchufar un monitor sin apagarlo: queda con geometría activa
        y el WM lo sigue viendo como un monitor real.
        """
        ...

    @abstractmethod
    def enable_outputs_auto(self, outputs: list[str]) -> None:
        ...

    @abstractmethod
    def disable_outputs(self, outputs: list[str]) -> None:
        ...
