from typing import Callable, Type

from assertme.base import Anything


class InstanceType(Anything):
    def __init__(self, _type: Type):
        super().__init__()
        self.type = _type

    def _check_methods(self) -> list[Callable]:
        return [self._check_instance]

    def _check_instance(self) -> bool:
        self.msg = f"Object is not an instance of {self.type.__name__}"
        return isinstance(self.other, self.type)
