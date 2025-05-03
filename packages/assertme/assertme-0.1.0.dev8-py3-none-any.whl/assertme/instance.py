from typing import Callable

from assertme.base import Anything


class InstanceType(Anything):
    def __init__(self, _type: type):
        super().__init__()
        self._type = _type

    def _check_methods(self) -> list[Callable]:
        return [self.__check_instance]

    def __check_instance(self) -> bool:
        """
        Check if the other object is an instance of the specified type.
        :return:
        """
        self.msg = f"Object is not an instance of {self._type.__name__}"
        return isinstance(self.other, self._type)
