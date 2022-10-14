"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from copy import deepcopy
from typing import Any, Optional

from validataclass.exceptions import InvalidTypeError
from .validator import Validator

__all__ = [
    'AllowEmptyString',
]


class AllowEmptyString(Validator):
    """
    Special validator that wraps another validator, but allows empty string ('') as input value.

    By default, the wrapper returns empty string ('') for empty string ('') as input value. Optionally a default value
    can be specified in the constructor that will be returned instead of empty string ('').

    If the wrapped validator raises an `InvalidTypeError`, `AllowEmptyString` will add str
    to its 'expected_types' parameter and reraise it.

    Examples:

    ```
    # Accepts strings and empty string (''), returns both unmodified (e.g. "foo" -> "foo", "" -> "")
    AllowEmptyString(StringValidator())

    # Accepts strings and empty string (''), returns a default string for empty string ('')
     (e.g. '' -> "no value given!", but "foo" -> "foo")
    AllowEmptyString(StringValidator(), default='no value given!')
    ```

    Valid input: `` or any data accepted by the wrapped validator
    Output: `` (or default value specified in constructor) or the output of the wrapped validator
    """

    # Default value returned in case the input is empty string ('')
    default_value: Any

    # Validator used in case the input is not empty string ('')
    wrapped_validator: Validator

    def __init__(self, validator: Validator, *, default: Any = ''):
        """
        Create a AllowEmptyString wrapper validator.

        Parameters:
            validator: Validator that will be wrapped (required)
            default: Value of any type that is returned instead of empty string ('') (default: ``)
        """
        # Check parameter validity
        if not isinstance(validator, Validator):
            raise TypeError('AllowEmptyString requires a Validator instance.')

        self.wrapped_validator = validator
        self.default_value = default

    def validate(self, input_data: Any, **kwargs) -> Optional[Any]:
        """
        Validate input data.

        If the input is empty string (''), return empty string ('') (or the value specified in the `default` parameter).
        Otherwise, pass the input to the wrapped validator and return its result.
        """
        if input_data == "":
            return deepcopy(self.default_value)

        try:
            # Call wrapped validator for all values other than empty string ('')
            return self.wrapped_validator.validate_with_context(input_data, **kwargs)
        except InvalidTypeError as error:
            # If wrapped validator raises an InvalidTypeError, add str to its 'expected_types' list and reraise it
            error.add_expected_type(str)
            raise error
