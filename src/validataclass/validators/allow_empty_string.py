"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from copy import deepcopy
from typing import Any, overload

from typing_extensions import Generic, TypeVar

from validataclass.exceptions import InvalidTypeError
from .validator import Validator

__all__ = [
    'AllowEmptyString',
]

# Type parameters for the validation result of the wrapped validator and for the default value (empty string by default)
T_WrappedValidated = TypeVar('T_WrappedValidated')
T_EmptyStringDefault = TypeVar('T_EmptyStringDefault', default=str)


class AllowEmptyString(
    Validator[T_WrappedValidated | T_EmptyStringDefault],
    Generic[T_WrappedValidated, T_EmptyStringDefault],
):
    """
    Special validator that wraps another validator, but allows empty strings as the input value.

    By default, the wrapper returns an empty string if the input value is an empty string. Alternatively, the parameter
    `default` can be set to a different value that will be returned instead of the empty string.

    If the wrapped validator raises an `InvalidTypeError`, the wrapper will add the type `str` to its `expected_types`
    and reraise the exception.

    Examples:

    ```
    # Accepts decimal strings and empty strings. Returns either a Decimal object or an empty string.
    # (e.g. '1.23' -> Decimal('1.23'), '' -> '')
    AllowEmptyString(DecimalValidator())

    # Accepts decimal strings and empty strings. If the input is an empty string, a Decimal(0) will be returned.
    # (e.g. '1.23' -> Decimal('1.23'), '' -> Decimal('0'))
    AllowEmptyString(DecimalValidator(), default=Decimal(0))
    ```

    Valid input: Empty string or any data accepted by the wrapped validator
    Output: Output of the wrapped validator or specified default value (default: empty string)
    """

    # Default value returned in case the input is empty string
    default_value: T_EmptyStringDefault

    # Validator used in case the input is not empty string
    wrapped_validator: Validator[T_WrappedValidated]

    @overload
    def __init__(self, validator: Validator[T_WrappedValidated], *, default: str = ''):
        ...

    @overload
    def __init__(self, validator: Validator[T_WrappedValidated], *, default: T_EmptyStringDefault):
        ...

    def __init__(self, validator: Validator[T_WrappedValidated], *, default: Any = ''):
        """
        Creates a `AllowEmptyString` wrapper validator.

        Parameters:
            `validator`: Validator that will be wrapped (required)
            `default`: Value of any type that is returned when the input is an empty string (default: empty string)
        """
        # Check parameter validity
        if not isinstance(validator, Validator):
            raise TypeError('AllowEmptyString requires a Validator instance.')

        self.wrapped_validator = validator
        self.default_value = default

    def validate(self, input_data: Any, **kwargs: Any) -> T_WrappedValidated | T_EmptyStringDefault:
        """
        Validates input data.

        If the input is an empty string, returns an empty string (or the value specified in the `default` parameter).
        Otherwise, pass the input to the wrapped validator and return its result.
        """
        if input_data == '':
            return deepcopy(self.default_value)

        try:
            # Call wrapped validator for all values other than empty string
            return self.wrapped_validator.validate_with_context(input_data, **kwargs)
        except InvalidTypeError as error:
            # If wrapped validator raises an InvalidTypeError, add str to its 'expected_types' list and reraise it
            error.add_expected_type(str)
            raise error
