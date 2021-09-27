# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import ValidationError

__all__ = [
    'InvalidEmailError',
]


class InvalidEmailError(ValidationError):
    """
    Validation error raised by `EmailValidator` when the input string is not a valid email address.
    """
    code = 'invalid_email'
