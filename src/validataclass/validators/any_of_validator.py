"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import warnings
from typing import Any, Iterable, List, Optional, Union

from validataclass.exceptions import ValueNotAllowedError, InvalidValidatorOptionException
from .validator import Validator

__all__ = [
    'AnyOfValidator',
]


class AnyOfValidator(Validator):
    """
    Validator that checks an input value against a specified list of allowed values. If the value is contained in the
    list, the value is returned.

    The allowed values can be specified with any iterable (e.g. a list, a set, a tuple, a generator expression, ...).

    The types allowed for input data will be automatically determined from the list of allowed values by default, unless
    explicitly specified with the parameter 'allowed_types'.

    By default, strings will be matched *case-insensitively*. To change this, set `case_sensitive=True`. The returned
    value will always be as defined in the list of allowed values (e.g. if the allowed values contain "Apple" and the
    validator is case-insensitive, then "APPLE" and "apple" will be valid input too, but in all cases "Apple" will be
    returned).

    NOTE: Prior to version 0.8.0, the validator was NOT case-insensitive by default. The old parameter "case_insensitive"
    still exists for compatibility, but is deprecated now and will be removed in a future version.

    If the input value is not valid (but has the correct type), a ValueNotAllowedError (code='value_not_allowed') will
    be raised. This error will include the list of allowed values (as "allowed_values"), as long as this list is not
    longer than 20 items. (This limit is defined in the attribute `max_allowed_values_in_validation_error`, which cannot
    be changed via parameters as of now, but can be changed by subclassing the validator and changing the value.)

    Examples:

    ```
    # Accepts "apple", "banana", "strawberry" in any capitalization (e.g. "APPLE" is accepted, but returns "apple")
    AnyOfValidator(['apple', 'banana', 'strawberry'])

    # Accepts the same values, but case-sensitively (e.g. "APPLE" is not accepted, only "apple" is)
    AnyOfValidator(['Apple', 'Banana', 'Strawberry'], case_sensitive=True)
    ```

    See also: `EnumValidator` (same principle but using Enum classes instead of raw value lists)

    Valid input: All values contained in allowed_values
    Output: Value as defined in allowed_values
    """

    # If the list of allowed values is longer than this value, do not include allowed values in ValueNotAllowedError
    max_allowed_values_in_validation_error: int = 20

    # Values allowed as input
    allowed_values: List[Any] = None

    # Types allowed for input data (set by parameter or autodetermined from allowed_values)
    allowed_types: List[type] = None

    # If set, strings will be matched case-sensitively
    case_sensitive: bool = False

    def __init__(
        self,
        allowed_values: Iterable[Any],
        *,
        allowed_types: Optional[Union[type, Iterable[type]]] = None,
        case_sensitive: Optional[bool] = None,
        case_insensitive: Optional[bool] = None,
    ):
        """
        Create an AnyOfValidator with a specified list of allowed values.

        Parameters:
            allowed_values: List (or any other iterable) of values that are allowed as input (required)
            allowed_types: Types that are allowed for input data (default: None, autodetermine types from allowed_values)
            case_sensitive: If set, strings will be matched case-sensitively (default: True)
            case_insensitive: DEPRECATED. Validator is case-insensitive by default, use case_sensitive to change this.
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

        # Changed in 0.8.0: The old "case_insensitive" parameter is now deprecated and replaced by a new parameter
        # "case_sensitive", which is True by default.
        # TODO: For version 1.0, remove the old parameter completely and set a real default value for the new parameter.
        if case_sensitive is not None and case_insensitive is not None:
            raise InvalidValidatorOptionException(
                'Parameters "case_sensitive" and "case_insensitive" (now deprecated) are mutually exclusive.'
            )
        elif case_insensitive is not None:
            warnings.warn(
                'The parameter "case_insensitive" is deprecated since version 0.8.0 and will be removed in the future. '
                'The AnyOfValidator and EnumValidator are now case-insensitive by default. To change this, set the new '
                'parameter "case_sensitive=False" instead.',
                DeprecationWarning
            )
            case_sensitive = not case_insensitive

        # Set case_sensitive parameter, defaulting to True.
        self.case_sensitive = case_sensitive if case_sensitive is not None else True

    def validate(self, input_data: Any, **kwargs) -> Any:
        """
        Validate that input is in the list of allowed values. Returns the value (as defined in the list).
        """
        # Special case to allow None as value if None is in the allowed_values list (bypasses _ensure_type())
        if None in self.allowed_values and input_data is None:
            return None

        # Ensure type is one of the allowed types (set by parameter or autodetermined from allowed_values)
        self._ensure_type(input_data, self.allowed_types)

        # Check if input is in the list of allowed values
        for allowed_value in self.allowed_values:
            if self._compare_values(input_data, allowed_value):
                return allowed_value

        # Invalid input (only include list of allowed values in validation error if the list is not too long)
        if len(self.allowed_values) <= self.max_allowed_values_in_validation_error:
            raise ValueNotAllowedError(allowed_values=self.allowed_values)
        else:
            raise ValueNotAllowedError()

    def _compare_values(self, input_value: Any, allowed_value: Any) -> bool:
        """
        Returns True if input value and allowed value are equal, in the sense of this validator (e.g. case-insensitively
        if that option is set).
        """
        # We need to make sure the check is typesafe (e.g. because 1 == True and 0 == False)
        if type(input_value) is not type(allowed_value):
            return False

        # Compare strings case-insensitively (unless case_sensitive option is set)
        if type(input_value) is str and not self.case_sensitive:
            return input_value.lower() == allowed_value.lower()
        else:
            return input_value == allowed_value
