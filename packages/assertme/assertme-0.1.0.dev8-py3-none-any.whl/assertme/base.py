from abc import ABC, abstractmethod
from typing import Any
from typing import Any as AnyType
from typing import Callable, Optional


class Anything(ABC):
    def __init__(self) -> None:
        """
        Initialize the ANY class.
        """
        self.msg = ""
        self.other: Optional[Any] = None

    def __eq__(self, other: AnyType) -> bool:
        """
        Check if the other object is equal to the ANY class.
        :param other:
        :return:
        """
        self.other = other
        return self.__fail_fast(
            [self.__check_not_none] + self._check_methods()
        )

    def __ne__(self, other) -> bool:
        """
        Check if the other object is not equal to the ANY class.
        :param other:
        :return:
        """
        return not self.__eq__(other)

    def __repr__(self) -> str:
        """
        Return a string representation of the ANY class.
        :return:
        """
        return f"<{self.__class__.__name__}({self.msg})>"

    @abstractmethod
    def _check_methods(self) -> list[Callable]:
        """
        Return a list of methods to check the equality of the object.
        :return:
        """
        raise NotImplementedError("Method _check_methods not implemented")

    def __check_not_none(self) -> bool:
        """
        Check if the other object is not None.
        :return:
        """
        self.msg = "Object is None"
        return self.other is not None

    def __fail_fast(self, checks: list[Callable]) -> bool:
        if result := all(check() for check in checks) is True:
            self.msg = ""
        return result
