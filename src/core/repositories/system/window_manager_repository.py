from abc import ABC, abstractmethod


class CoreWindowManagerRepository(ABC):
    @abstractmethod
    def list_monitors(self) -> list[str]:
        ...

    @abstractmethod
    def set_monitor_desktops(self, monitor: str, desktops: list[str]) -> None:
        ...

    @abstractmethod
    def list_desktops(self) -> list[str]:
        ...

    @abstractmethod
    def focus_desktop(self, desktop: str) -> None:
        ...

    @abstractmethod
    def list_window_ids(self) -> list[str]:
        ...

    @abstractmethod
    def window_class(self, window_id: str) -> list[str]:
        """Tokens de WM_CLASS de la ventana (instancia y clase), o [] si falla."""
        ...

    @abstractmethod
    def desktop_of_window(self, window_id: str) -> str | None:
        ...

    @abstractmethod
    def move_window_to_desktop(self, window_id: str, desktop: str) -> None:
        ...

    @abstractmethod
    def add_one_shot_rule(self, wm_class: str, desktop: str) -> None:
        """Regla one-shot del WM: la próxima ventana de esa clase nace en ese desktop."""
        ...

    @abstractmethod
    def remove_rules(self, wm_class: str) -> None:
        """Borra reglas pendientes de esa clase (limpieza si la one-shot no se consumió)."""
        ...
