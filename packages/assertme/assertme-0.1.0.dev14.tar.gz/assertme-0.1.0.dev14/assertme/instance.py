from typing import Annotated, Type, Union

from pydantic import Strict

from assertme.pydantic import WithPydantic


class InstanceOf(WithPydantic):
    instance_type: Union[Type, tuple[Type]]

    def __init__(self, instance_type: Union[Type, tuple[Type]]):
        super().__init__(Annotated[instance_type, Strict])
