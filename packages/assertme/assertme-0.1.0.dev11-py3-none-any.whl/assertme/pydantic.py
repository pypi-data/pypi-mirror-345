from typing import Callable

from pydantic import TypeAdapter

from assertme.base import Anything


class WithPydantic(Anything):
    validator: TypeAdapter

    def __init__(self, wtf):
        super().__init__()
        self.validator = TypeAdapter(wtf)

    def _check_methods(self) -> list[Callable]:
        return [self._check_pydantic]

    def _check_pydantic(self) -> bool:
        try:
            self.validator.validate_python(self.other)
            return True
        except Exception as e:
            self.msg = f"Field is not as defined: {e}"
            return False
