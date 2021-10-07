"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from validataclass.exceptions import ValidationError

__all__ = [
    'RegexMatchError',
]


class RegexMatchError(ValidationError):
    """
    Validation error raised by `RegexValidator` when the input string does not match the regular expression.
    """
    code = 'invalid_string_format'
