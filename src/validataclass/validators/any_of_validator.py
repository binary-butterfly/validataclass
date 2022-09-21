"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Iterable, List, Optional, Union

from validataclass.exceptions import ValueNotAllowedError, InvalidValidatorOptionException
from .validator import Validator

__all__ = [
    'AnyOfValidator',
]


class AnyOfValidator(Validator):
    """
    Validator that checks an input value against a specified list of allowed values. If the value is contained in the
    list, the value is returned unmodified.

    The allowed values can be specified with any iterable (e.g. a list, a set, a tuple, a generator expression, ...).

    The types allowed for input data will be automatically determined from the list of allowed values by default, unless
    explicitly specified with the parameter 'allowed_types'.

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

    def __init__(self, allowed_values: Iterable[Any], *, allowed_types: Optional[Union[type, Iterable[type]]] = None):
        """
        Create an AnyOfValidator with a specified list of allowed values.

        Parameters:
            allowed_values: List (or any other iterable) of values that are allowed as input (required)
            allowed_types: Types that are allowed for input data (default: None, autodetermine types from allowed_values)
        """
        # Save list of allowed values
        self.allowed_values = list(allowed_values)

        # Determine allowed data types from allowed values unless allowed_types is set
        if allowed_types is None:
            self.allowed_types = list(set(type(value) for value in self.allowed_values))
        elif not isinstance(allowed_types, Iterable):
            self.allowed_types = [allowed_types]
        else:
            self.allowed_types = list(allowed_types)

        # Check that list of allowed types is not empty
        if len(self.allowed_types) == 0:
            raise InvalidValidatorOptionException('Parameter "allowed_types" is an empty list (or types could not be autodetermined).')

    def validate(self, input_data: Any, **kwargs) -> Any:
        """
        Validate that input is in the list of allowed values. Returns the value unmodified.
        """
        # Special case to allow None as value if None is in the allowed_values list (bypasses _ensure_type())
        if None in self.allowed_values and input_data is None:
            return None

        # Ensure type is one of the allowed types (set by parameter or autodetermined from allowed_values)
        self._ensure_type(input_data, self.allowed_types)

        # Check if input is in the list of allowed values
        if not self._is_allowed_value(input_data):
            raise ValueNotAllowedError()

        return input_data

    def _is_allowed_value(self, input_value: Any):
        """
        Checks if an input value is in the list of allowed values.
        """
        # Note: We cannot simply use the "in" operator here because it's not fully typesafe for integers and booleans. (See issue #1.)
        # (E.g. all of the following expressions are True according to Python: 1 in [True], 0 in [False], True in [1], False in [0])
        for value in self.allowed_values:
            if type(input_value) is type(value) and input_value == value:
                return True
        return False
