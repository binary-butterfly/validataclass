# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from .validator import Validator


class IntegerValidator(Validator):
    """
    Validator for integer values.

    Valid input: `int`
    Output: `int`
    """
    def validate(self, input_data: Any) -> int:
        self._ensure_type(input_data, int)
        return int(input_data)
