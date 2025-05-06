import abc
from collections.abc import Generator
from typing import Protocol, runtime_checkable


@runtime_checkable
class RpmDBInterfaceProtocol(Protocol):
    def read(self) -> Generator[bytes, None, None]: ...


class RpmDBInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls: type["RpmDBInterface"], subclass: object) -> bool:
        return bool(isinstance(subclass, RpmDBInterfaceProtocol))

    @abc.abstractmethod
    def read(
        self,
    ) -> Generator[bytes, None, None]:
        """Read entry bytes."""
        raise NotImplementedError
