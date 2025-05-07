from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Strict


StrictUUID = Annotated[UUID, Strict]
StrictDatetime = Annotated[datetime, Strict]
