# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import ValidationError

__all__ = [
    'EnumInvalidValueError',
]


class EnumInvalidValueError(ValidationError):
    """
    Validation error raised by `EnumValidator` when the input data is not a valid value for the given Enum.
    """
    code = 'enum_invalid_value'
