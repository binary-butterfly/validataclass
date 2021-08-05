# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import deepcopy
from typing import Any, Optional

from .validator import Validator


class Noneable(Validator):
    """
    Helper validator that wraps another validator but allows `None` as input value.

    By default, the wrapper returns `None` for `None` as input value. Optionally a default value can be specified
    in the constructor that will be returned instead of `None`.

    Examples:
        Noneable(StringValidator())
        Noneable(StringValidator(), default='no value given!')

    Valid input: `None` or any data accepted by the wrapped validator
    Output: `None` (or default value specified in constructor) or the output of the wrapped validator
    """
    default_value: Any
    wrapped_validator: Validator

    def __init__(self, validator: Validator, *, default: Any = None):
        self.wrapped_validator = validator
        self.default_value = default

    def validate(self, input_data: Any) -> Optional[Any]:
        if input_data is None:
            return deepcopy(self.default_value)

        return self.wrapped_validator.validate(input_data)
