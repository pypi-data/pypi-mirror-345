from datetime import datetime, tzinfo
from typing import Callable, Optional, cast

from dateutil.parser import parse

from assertme.base import Anything


class AnyDatetime(Anything):
    other: datetime
    future: Optional[bool]
    tz: Optional[tzinfo]

    def __init__(
        self, future: Optional[bool] = None, tz: Optional[tzinfo] = None
    ) -> None:
        super().__init__()
        self.future: Optional[bool] = future
        self.tz: Optional[tzinfo] = tz

    def _check_methods(self) -> list[Callable]:
        return [
            self._check_instance_type,
            self._check_date_range,
            self._check_tzinfo,
        ]

    def _check_instance_type(self) -> bool:
        self.msg = "Date should be datetime type"
        return isinstance(self.other, datetime)

    def _check_date_range(self) -> bool:
        if self.future is None or self.other is None:
            return True

        if self.future and self.other < datetime.now(self.other.tzinfo):
            self.msg = "Date should be in the future"
            return False

        if not self.future and self.other >= datetime.now(self.other.tzinfo):
            self.msg = "Date should be in the past"
            return False

        return True

    def _check_tzinfo(self) -> bool:
        self.msg = (
            f"Date should be in tzinfo={self.tz} and it was tzinfo={self.other.tzinfo}"
        )
        # Supports both datetime and dateutil timezones
        return (
            datetime.now(self.other.tzinfo).utcoffset()
            == datetime.now(self.tz).utcoffset()
        )


class AnyStrDatetime(AnyDatetime):
    strptime: Optional[str]

    def __init__(self, strptime: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strptime = strptime

    def _check_methods(self) -> list[Callable]:
        return [self._parse] + super()._check_methods()

    def _parse(self) -> bool:
        try:
            if self.strptime:
                self.other = datetime.strptime(cast(str, self.other), self.strptime)
            else:
                self.other = parse(cast(str, self.other))
            return True
        except Exception as e:
            self.msg = f"Date is not in the correct format: {e}"
            return False
