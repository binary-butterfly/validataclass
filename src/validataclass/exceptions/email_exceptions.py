"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from .base_exceptions import ValidationError

__all__ = [
    'InvalidEmailError',
]


class InvalidEmailError(ValidationError):
    """
    Validation error raised by `EmailValidator` when the input string is not a valid email address.
    """
    code = 'invalid_email'
