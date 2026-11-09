"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any
from uuid import UUID

from typing_extensions import override

from .validator import Validator

__all__ = [
    'UUIDValidator',
]

from ..exceptions.uuid_exceptions import InvalidUUIDError


class UUIDValidator(Validator[UUID]):
    """
    Validator for UUIDs.

    Valid input: `str`
    Output: `UUID`
    """

    @override
    def validate(self, input_data: Any, **kwargs: Any) -> UUID:
        self._ensure_type(input_data, str)

        # Cast to string (for type hinting)
        input_str = str(input_data)

        try:
            return UUID(input_str)
        except ValueError as e:
            raise InvalidUUIDError from e
