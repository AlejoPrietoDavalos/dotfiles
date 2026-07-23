from abc import ABC, abstractmethod
from typing import Literal

MediaPlayerAction = Literal["previous", "next", "play_pause", "stop"]


class CoreMediaPlayerRepository(ABC):
    @abstractmethod
    def run(self, action: MediaPlayerAction) -> None:
        ...

    @abstractmethod
    def previous(self) -> None:
        ...

    @abstractmethod
    def next(self) -> None:
        ...

    @abstractmethod
    def play_pause(self) -> None:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...
