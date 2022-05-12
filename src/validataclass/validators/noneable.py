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
    'Noneable',
]


class Noneable(Validator):
    """
    Special validator that wraps another validator, but allows `None` as input value.

    By default, the wrapper returns `None` for `None` as input value. Optionally a default value can be specified in the
    constructor that will be returned instead of `None`.

    If the wrapped validator raises an `InvalidTypeError`, `Noneable` will add 'none' to its 'expected_types' parameter
    and reraise it.

    Examples:

    ```
    # Accepts strings and None, returns both unmodified (e.g. "foo" -> "foo", "" -> "", None -> None)
    Noneable(StringValidator())

    # Accepts strings and None, returns a default string for None (e.g. None -> "no value given!", but "" -> "")
    Noneable(StringValidator(), default='no value given!')
    ```

    See also: `NoneToUnsetValue`

    Valid input: `None` or any data accepted by the wrapped validator
    Output: `None` (or default value specified in constructor) or the output of the wrapped validator
    """

    # Default value returned in case the input is None
    default_value: Any

    # Validator used in case the input is not None
    wrapped_validator: Validator

    def __init__(self, validator: Validator, *, default: Any = None):
        """
        Create a Noneable wrapper validator.

        Parameters:
            validator: Validator that will be wrapped (required)
            default: Value of any type that is returned instead of None (default: None)
        """
        # Check parameter validity
        if not isinstance(validator, Validator):
            raise TypeError('Noneable requires a Validator instance.')

        self.wrapped_validator = validator
        self.default_value = default

    def validate(self, input_data: Any) -> Optional[Any]:
        """
        Validate input data.

        If the input is None, return None (or the value specified in the `default` parameter). Otherwise, pass the input
        to the wrapped validator and return its result.
        """
        if input_data is None:
            return deepcopy(self.default_value)

        try:
            # Call wrapped validator for all values other than None
            return self.wrapped_validator.validate(input_data)
        except InvalidTypeError as error:
            # If wrapped validator raises an InvalidTypeError, add 'none' to its 'expected_types' list and reraise it
            error.add_expected_type(type(None))
            raise error
