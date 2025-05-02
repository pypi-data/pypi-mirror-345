from datetime import datetime
from typing import Union, Callable, Optional

from dateutil.parser import parse

from assertme.base import Anything


class AnyDatetime(Anything):
    def __init__(self, future=None, tzinfo=None) -> None:
        """
        Initialize the ANY_DATETIME class.
        """
        super().__init__()
        self.future: Optional[bool] = future
        self.tzinfo: Optional[tzinfo] = tzinfo

    def _check_methods(self) -> list[Callable]:
        """
        Return a list of methods to check the equality of the object.
        :return:
        """
        return [
            self.__check_date_range,
            self.__check_tzinfo,
        ]

    def __check_date_range(self) -> bool:
        """
        Check if the date is in the future or not.
        :param future:
        :return:
        """
        if self.future is True and self.other < datetime.now(
            self.other.tzinfo
        ):
            self.msg = "Date should be in the future"
            return False

        if self.future is False and self.other >= datetime.now(
            self.other.tzinfo
        ):
            self.msg = "Date should be in the past"
            return False

        return True

    def __check_tzinfo(self) -> bool:
        """
        Check if the date has the correct tzinfo.
        :param tzinfo:
        :return:
        """
        self.msg = f"Date should be in tzinfo={self.tzinfo}"
        return self.other.tzinfo == self.tzinfo


class AnyStrDatetime(AnyDatetime):
    def _check_methods(self) -> list[Callable]:
        """
        Return a list of methods to check the equality of the object.
        :return:
        """
        return [self.__parse_date] + super()._check_methods()

    def __parse_date(self) -> Union[datetime, bool]:
        """
        Parse the date string into a datetime object.
        :param date:
        :return:
        """
        try:
            self.other = parse(self.other)
            return True
        except Exception as e:
            self.msg = f"Date is not in the correct format: {e}"
            return False
