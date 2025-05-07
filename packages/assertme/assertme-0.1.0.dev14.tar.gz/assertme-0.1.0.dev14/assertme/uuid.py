from typing import Annotated, Optional, _SpecialForm
from uuid import UUID

from pydantic import StrictStr
from pydantic.types import UuidVersion

from assertme import WithPydantic
from assertme.annotations import StrictUUID


class _UUIDVersion:
    @staticmethod
    def _uuid_by_version(version) -> _SpecialForm | type[UUID]:
        if version is None:
            return UUID
        return Annotated[UUID, UuidVersion(version)]


class AnyStrUUID(WithPydantic, _UUIDVersion):
    def __init__(self, version: Optional[int] = None):
        super().__init__([StrictStr, self._uuid_by_version(version)])


class AnyUUID(WithPydantic, _UUIDVersion):
    def __init__(self, version: Optional[int] = None):
        super().__init__([StrictUUID, self._uuid_by_version(version)])
