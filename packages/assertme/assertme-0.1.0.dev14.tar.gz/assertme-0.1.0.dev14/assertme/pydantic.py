from typing import Any, Callable

from pydantic import TypeAdapter

from assertme.base import Anything


class WithPydantic(Anything):
    validators: list[TypeAdapter]
    strict: bool

    def __init__(self, field: list | Any, strict=False):
        super().__init__()
        fields = field if isinstance(field, list) else [field]
        self.validators = [TypeAdapter(f) for f in fields]
        self.strict = strict

    def _check_methods(self) -> list[Callable]:
        return [self._check_pydantic]

    def _check_pydantic(self) -> bool:
        try:
            [validator.validate_python(self.other) for validator in self.validators]
            return True
        except Exception as e:
            self.msg = f"Field is not as defined: {e}"
            return False
