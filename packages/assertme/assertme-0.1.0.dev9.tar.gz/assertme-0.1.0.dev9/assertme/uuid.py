from typing import Callable, Optional
from uuid import UUID

from assertme.base import Anything


class AnyUuid(Anything):
    def __init__(self, version: Optional[int] = None):
        super().__init__()
        self.version = version

    def _check_methods(self) -> list[Callable]:
        return [self._check_instance, self._check_version]

    def _check_instance(self) -> bool:
        self.msg = f"Object is not type of {type(UUID)}"
        return isinstance(self.other, UUID)

    def _check_version(self) -> bool:
        self.msg = f"UUID({self.other.version}) is not version {self.version}"
        return self.other.version == self.version if self.version else True


class AnyStrUuid(AnyUuid):
    def _check_methods(self) -> list[Callable]:
        return [self._parse] + super()._check_methods()

    def _parse(self) -> bool:
        try:
            self.other = UUID(self.other)
            return True
        except Exception as e:
            self.msg = f"UUID is not in the correct format: {e}"
            return False
