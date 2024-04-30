"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Optional

from .base_exceptions import ValidationError

__all__ = [
    'NumberRangeError',
    'DecimalPlacesError',
    'InvalidIntegerError',
    'InvalidDecimalError',
    'NonFiniteNumberError',
]


class NumberRangeError(ValidationError):
    """
    Validation error raised by number validators (e.g. `IntegerValidator`, `DecimalValidator`, ...) when a number range
    requirement (minimal and/or maximal value) is specified and the input does not match those requirements.

    May contain the extra fields `min_value` and `max_value`, depending on which are specified. The type of these fields
    depends on the validator, e.g. an `IntegerValidator` sets integers, while a `DecimalValidator` sets decimal strings.
    """
    code = 'number_range_error'

    def __init__(self, *, min_value: Optional[Any] = None, max_value: Optional[Any] = None, **kwargs: Any):
        if min_value is not None:
            kwargs.update(min_value=min_value)
        if max_value is not None:
            kwargs.update(max_value=max_value)
        super().__init__(**kwargs)


class DecimalPlacesError(ValidationError):
    """
    Validation error raised by `DecimalValidator` when a minimum or maximum number of decimal places is specified and
    the input number has too many or too little decimal places.

    May contain the extra fields `min_places` and `max_places` (integers), depending on which are specified.
    """
    code = 'decimal_places'

    def __init__(self, *, min_places: Optional[Any] = None, max_places: Optional[Any] = None, **kwargs: Any):
        if min_places is not None:
            kwargs.update(min_places=min_places)
        if max_places is not None:
            kwargs.update(max_places=max_places)
        super().__init__(**kwargs)


class InvalidIntegerError(ValidationError):
    """
    Validation error raised by `IntegerValidator` with `allow_strings=True` when an input string cannot be parsed as an
    integer value, i.e. the string contains invalid characters or is empty.
    """
    code = 'invalid_integer'


class InvalidDecimalError(ValidationError):
    """
    Validation error raised by `DecimalValidator` when an input string cannot be parsed as a decimal value, i.e. the
    string is malformed.
    """
    code = 'invalid_decimal'


class NonFiniteNumberError(ValidationError):
    """
    Validation error raised by `FloatValidator` (and subclasses) when an input string can be parsed as a float, but does
    not have a finite value (i.e. it is either `(+/-)Infinity` or `NaN`).
    """
    code = 'not_a_finite_number'
