# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal, InvalidOperation
from typing import Any

from .string_validator import StringValidator
from wtfjson.exceptions import ValidationError


class DecimalValidator(StringValidator):
    """
    Validator that parses decimal values.

    Valid input: `str` in a format accepted by `decimal.Decimal`
    Output: `decimal.Decimal`
    """
    def validate(self, input_data: Any) -> Decimal:
        # First, validate input data as string
        decimal_string = super().validate(input_data)

        try:
            # Now, try to parse string as decimal value
            return Decimal(decimal_string)
        except InvalidOperation:
            raise ValidationError(code='invalid_decimal')
