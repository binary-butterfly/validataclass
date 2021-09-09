# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Union, List

from .validator import Validator
from wtfjson.exceptions import ValueNotAllowedError, InvalidValidatorOptionException

__all__ = [
    'AnyOfValidator',
]


class AnyOfValidator(Validator):
    """
    Validator that checks an input value against a specified list of allowed values. If the value is contained in the list, the value
    is returned unmodified.

    The types allowed for input data will be automatically determined from the list of allowed values by default, unless explicitly
    specified with the parameter 'allowed_types'.

    Examples:

    ```
    AnyOfValidator(['apple', 'banana', 'strawberry'])
    ```

    See also: `EnumValidator` (same principle but using Enum classes instead of raw value lists)

    Valid input: All values contained in allowed_values
    Output: Unmodified input (if valid)
    """

    # Values allowed as input
    allowed_values: List[Any] = None

    # Types allowed for input data (set by parameter or autodetermined from allowed_values)
    allowed_types: List[type] = None

    def __init__(self, allowed_values: List[Any], *, allowed_types: Union[type, List[type]] = None):
        """
        Create an AnyOfValidator with a specified list of allowed values.

        Parameters:
            allowed_values: List of values (of any type) allowed as input (required)
            allowed_types: List of types allowed for input data (default: None, autodetermine types from allowed_values)
        """
        # Determine allowed data types from allowed values unless allowed_types is set
        if allowed_types is None:
            allowed_types = list(set(type(value) for value in allowed_values))
        elif type(allowed_types) is not list:
            allowed_types = [allowed_types]

        # Check that list of allowed types is not empty
        if len(allowed_types) == 0:
            raise InvalidValidatorOptionException('Parameter "allowed_types" is an empty list (or types could not be autodetermined).')

        # Save parameters
        self.allowed_values = allowed_values
        self.allowed_types = allowed_types

    def validate(self, input_data: Any) -> Any:
        """
        Validate that input is in the list of allowed values. Returns the value unmodified.
        """
        # Special case to allow None as value if None is in the allowed_values list (bypasses _ensure_type())
        if None in self.allowed_values and input_data is None:
            return None

        # Ensure type is one of the allowed types (set by parameter or autodetermined from allowed_values)
        self._ensure_type(input_data, self.allowed_types)

        # Check if input is in the list of allowed values
        if input_data not in self.allowed_values:
            raise ValueNotAllowedError()

        return input_data
