# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Optional

from wtfjson.exceptions import ValidationError


class NumberRangeError(ValidationError):
    """
    Validation error raised by number validators (e.g. `IntegerValidator`, `DecimalValidator`, ...) when a number range requirement
    (minimal and/or maximal value) is specified and the input does not match those requirements.

    May contain the extra fields 'min_value' and 'max_value', depending on which are specified. The type of these fields depends on
    the validator, e.g. an IntegerValidator sets integers, while a DecimalValidator sets decimal strings.
    """
    code = 'number_range_error'

    def __init__(self, *, min_value: Optional[Any] = None, max_value: Optional[Any] = None, **kwargs):
        min_value_args = {'min_value': min_value} if min_value is not None else {}
        max_value_args = {'max_value': max_value} if max_value is not None else {}
        super().__init__(**min_value_args, **max_value_args, **kwargs)
