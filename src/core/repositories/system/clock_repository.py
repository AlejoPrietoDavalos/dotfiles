from abc import ABC, abstractmethod


class CoreClockRepository(ABC):
    @abstractmethod
    def set_timezone(self, timezone: str) -> None:
        ...

    @abstractmethod
    def sync_system_to_hardware(self) -> None:
        ...
