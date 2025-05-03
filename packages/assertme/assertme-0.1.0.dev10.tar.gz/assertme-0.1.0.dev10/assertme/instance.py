from typing import Callable, Type

from assertme.base import Anything


class InstanceType(Anything):
    instance_type: Type

    def __init__(self, instance_type: Type):
        super().__init__()
        self.instance_type = instance_type

    def _check_methods(self) -> list[Callable]:
        return [self._check_instance]

    def _check_instance(self) -> bool:
        self.msg = f"Object is not an instance of {self.instance_type.__name__}"
        return isinstance(self.other, self.instance_type)
