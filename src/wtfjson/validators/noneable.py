# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from typing import Any, Optional

from .validator import Validator
from wtfjson.exceptions import InvalidTypeError

__all__ = [
    'Noneable',
]


class Noneable(Validator):
    """
    Helper validator that wraps another validator but allows `None` as input value.

    By default, the wrapper returns `None` for `None` as input value. Optionally a default value can be specified in the constructor
    that will be returned instead of `None`.

    If the wrapped validator raises an `InvalidTypeError`, `Noneable` will add 'none' to its 'expected_types' parameter and reraise it.

    Examples:
        Noneable(StringValidator())
        Noneable(StringValidator(), default='no value given!')

    Valid input: `None` or any data accepted by the wrapped validator
    Output: `None` (or default value specified in constructor) or the output of the wrapped validator
    """

    # Default value returned in case the input is None
    default_value: Any
    # Validator used in case the input is not None
    wrapped_validator: Validator

    def __init__(self, validator: Validator, *, default: Any = None):
        self.wrapped_validator = validator
        self.default_value = default

    def validate(self, input_data: Any) -> Optional[Any]:
        if input_data is None:
            return deepcopy(self.default_value)

        try:
            # Call wrapped validator for all values other than None
            return self.wrapped_validator.validate(input_data)
        except InvalidTypeError as error:
            # If wrapped validator raises an InvalidTypeError, add 'none' to its 'expected_types' list and reraise it
            error.add_expected_type(type(None))
            raise error
