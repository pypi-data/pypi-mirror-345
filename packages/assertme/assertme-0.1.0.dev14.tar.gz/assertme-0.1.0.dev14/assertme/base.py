from abc import ABC, abstractmethod
from typing import Any, Callable


class Anything(ABC):
    msg: str
    other: Any

    def __init__(self) -> None:
        self.msg = ""

    def __eq__(self, other: Any) -> bool:
        self.other = other
        return self.__fail_fast([self._check_not_none] + self._check_methods())

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}({self.msg})>"

    @abstractmethod
    def _check_methods(self) -> list[Callable]:
        raise NotImplementedError()

    def _check_not_none(self) -> bool:
        self.msg = "Object is None"
        return self.other is not None

    def __fail_fast(self, checks: list[Callable]) -> bool:
        if result := all(check() for check in checks) is True:
            self.msg = ""
        return result
