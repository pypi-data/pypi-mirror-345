from typing import Callable

from assertme.base import Anything


class AnyInt(Anything):
    def _check_methods(self) -> list[Callable]:
        return [self._check_instance]

    def _check_instance(self) -> bool:
        """
        Check if the other object is an instance of int.
        :return:
        """
        self.msg = "Object is not an instance of int"
        return isinstance(self.other, int)


ANY_INT = AnyInt()
