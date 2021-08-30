# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import ValidationError

__all__ = [
    'RegexMatchError',
]


class RegexMatchError(ValidationError):
    """
    Validation error raised by `RegexException` when the input string does not match the regular expression.
    """
    code = 'invalid_string_format'
