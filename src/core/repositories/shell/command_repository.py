from abc import ABC, abstractmethod


class CoreCommandRepository(ABC):
    """Contract for command execution used by infrastructure drivers.

    This abstraction lives in core so program/file/pkg repositories can execute
    system commands without depending on `subprocess` directly. Typical usage:
    concrete repositories in `app/drivers/repositories/*`.

    Solo API por argv (shell=False): no se expone ejecución por string de shell
    para evitar command injection al interpolar valores.
    """

    @abstractmethod
    def run_argv(self, argv: list[str]) -> None:
        """Run a command by argv tokens (shell=False style)."""
        ...

    @abstractmethod
    def run_argv_capture(self, argv: list[str]) -> str:
        """Run argv command and return stdout."""
        ...

    @abstractmethod
    def run_argv_quiet(self, argv: list[str]) -> int:
        """Run argv command discarding output and return exit code."""
        ...

    @abstractmethod
    def command_exists(self, name: str) -> bool:
        """Check whether a command is available in PATH."""
        ...
