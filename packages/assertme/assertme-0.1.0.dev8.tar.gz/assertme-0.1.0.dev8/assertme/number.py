from typing import Callable, Generic, Optional, Type, TypeVar, Union

from assertme.base import Anything


NUMBER_TYPES = [int, float]
T = TypeVar("T", bound=Union[int, float])


class AnyNumber(Anything, Generic[T]):
    def __init__(
        self,
        instance_type: Optional[Type[T]] = None,
        gt: Optional[T] = None,
        lt: Optional[T] = None,
    ):
        super().__init__()
        self.instance_type = instance_type or tuple(NUMBER_TYPES)
        self.gt = gt
        self.lt = lt

    def _check_methods(self) -> list[Callable]:
        return [self._check_instance, self._check_lt, self._check_gt]

    def _check_instance(self) -> bool:
        self.msg = (
            f"Type is {type(self.other)} instead of {self.instance_type}"
        )
        return isinstance(self.other, self.instance_type)

    def _check_lt(self):
        self.msg = f"Number({self.other}) should be less than {self.lt}"
        return self.other <= self.lt if self.lt is not None else True

    def _check_gt(self):
        self.msg = f"Number({self.other}) should be greater than {self.gt}"
        return self.other >= self.gt if self.gt is not None else True
