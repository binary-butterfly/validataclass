"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Optional

from validataclass.exceptions import ValidationError

__all__ = [
    'ValueNotAllowedError',
]


# Collection of exceptions for validators that don't have their own _exceptions.py

class ValueNotAllowedError(ValidationError):
    """
    Validation error raised by `AnyOfValidator` and `EnumValidator` when the input value is not an element in the
    specified list of allowed values.
    """
    code = 'value_not_allowed'

    def __init__(self, *, allowed_values: Optional[list] = None, **kwargs):
        super().__init__(allowed_values=allowed_values, **kwargs)
