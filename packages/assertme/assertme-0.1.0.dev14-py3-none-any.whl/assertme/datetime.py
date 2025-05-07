from dataclasses import dataclass
from datetime import datetime, tzinfo
from typing import Annotated, Any, Callable, Optional, _SpecialForm

from pydantic import (
    FutureDatetime,
    NaiveDatetime,
    PastDatetime,
    StrictStr,
)
from pydantic_core.core_schema import no_info_wrap_validator_function

from assertme.annotations import StrictDatetime
from assertme.pydantic import WithPydantic


class _DatetimeValidators:
    @staticmethod
    def _validators(
        future: Optional[bool] = None, tz: Optional[tzinfo] = None
    ) -> list[type | _SpecialForm]:
        validators: list[type | _SpecialForm] = []
        if future is True:
            validators.append(FutureDatetime)

        if future is False:
            validators.append(PastDatetime)

        if tz is None:
            validators.append(NaiveDatetime)
        else:
            validators.append(Annotated[datetime, TZValidator(tz)])

        return validators


class AnyDatetime(WithPydantic, _DatetimeValidators):
    def __init__(self, **kwargs) -> None:
        super().__init__([StrictDatetime, *self._validators(**kwargs)])


class AnyStrDatetime(WithPydantic, _DatetimeValidators):
    def __init__(self, **kwargs):
        super().__init__([StrictStr, *self._validators(**kwargs)])


@dataclass(frozen=True)
class TZValidator:
    tz: tzinfo | None = None

    def tz_constraint_validator(
        self, value: datetime, handler: Callable[[datetime], datetime]
    ) -> datetime:
        result = handler(value)

        if self.tz is not None:
            assert (
                datetime.now(result.tzinfo).utcoffset()
                == datetime.now(self.tz).utcoffset()
            ), f"Invalid tzinfo: {str(result.tzinfo)}, expected: {self.tz}"

        return result

    def __get_pydantic_core_schema__(self, source_type: Any, handler: Any) -> Any:
        return no_info_wrap_validator_function(
            self.tz_constraint_validator,
            handler(source_type),
        )
