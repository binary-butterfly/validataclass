# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import ValidationError

__all__ = [
    'InvalidUrlError',
]


class InvalidUrlError(ValidationError):
    """
    Validation error raised by `UrlValidator` when the input string is not a valid URL (as defined by the validator options).
    """
    code = 'invalid_url'
