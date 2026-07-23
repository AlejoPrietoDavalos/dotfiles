from abc import ABC, abstractmethod


class CoreKeyboardRepository(ABC):
    @abstractmethod
    def set_layout(self, layout: str) -> None:
        ...
