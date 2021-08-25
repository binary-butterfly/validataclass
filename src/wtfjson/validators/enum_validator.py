# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum, EnumMeta
from typing import Any, Type, Union

from .validator import Validator
from wtfjson.exceptions import EnumInvalidValueError, InvalidValidatorOptionException

__all__ = [
    'EnumValidator',
]


class EnumValidator(Validator):
    """
    Validator that uses an Enum class to parse input (strings or integers) to members of that enumeration.

    The types allowed for input data can be explicitly specified with the parameter 'allowed_types'. Currently only `str` and `int`
    are supported. If not specified, the types will be automatically determined from the values of the Enum.

    Examples:

    ```
    EnumValidator(ExampleEnum)

    # Only allow strings as input, regardless of the enum's values
    EnumValidator(ExampleEnum, allowed_types=[str])
    ```

    Valid input: `str` or `int` (depending on 'allowed_types' and the enum values)
    Output: Member of specified Enum class
    """

    # Enum class used by validator
    enum_cls: Type[Enum]

    # Types allowed for input data (set by parameter or autodetermined from enum values)
    allowed_types: list[type] = None

    def __init__(self, enum_cls: Type[Enum], *, allowed_types: Union[type, list[type]] = None):
        """
        Create a EnumValidator for a specified Enum class.

        Parameters:
            enum_cls: Enum class to use for validation (required)
            allowed_types: List of types allowed for input data (default: None, autodetermine types from enum values)
        """
        # Ensure parameter is an Enum class
        if not isinstance(enum_cls, EnumMeta):
            raise InvalidValidatorOptionException('Parameter "enum_cls" must be an Enum class.')

        # Determine allowed data types from enum values unless allowed_types is set
        if allowed_types is None:
            allowed_types = list(set(type(member.value) for member in enum_cls))
        elif type(allowed_types) is not list:
            allowed_types = [allowed_types]

        # Check that list of allowed types is not empty
        if len(allowed_types) == 0:
            raise InvalidValidatorOptionException('Parameter "allowed_types" is an empty list (or types could not be autodetermined)!')

        # Only allow strings and integer as values (for now, might be extended later)
        for t in allowed_types:
            if t not in [str, int]:
                raise InvalidValidatorOptionException(f'Parameter "allowed_types" contains unsupported type "{t.__name__}".')

        # Save parameters
        self.enum_cls = enum_cls
        self.allowed_types = allowed_types

    def validate(self, input_data: Any) -> Enum:
        """
        Validate input to be a valid value of the specified Enum. Returns the Enum member.
        """
        # Ensure type is one of the allowed types (set by parameter or autodetermined from enum values)
        self._ensure_type(input_data, self.allowed_types)

        # Try to convert value to enum member
        try:
            return self.enum_cls(input_data)
        except ValueError:
            raise EnumInvalidValueError()
