# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any

from .validator import Validator


class StringValidator(Validator):
    """
    Validator for arbitrary strings.

    Valid input: `str`
    Output: `str`
    """
    def validate(self, input_data: Any) -> str:
        self._ensure_type(input_data, str)
        return str(input_data)
