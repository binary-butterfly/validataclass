from typing import Any

from validataclass.exceptions import ValidationError


class InvalidUUIDError(ValidationError):
    """
    Validation error raised by `UUIDValidator` when input is not a valid UUID.
    """
    code = 'invalid_uuid'

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
