"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Optional

from .base_exceptions import ValidationError

__all__ = [
    'StringInvalidLengthError',
    'StringTooShortError',
    'StringTooLongError',
    'StringInvalidCharactersError',
]


class StringInvalidLengthError(ValidationError):
    """
    Base class for `StringTooShortError` and `StringTooLongError`, raised by `StringValidator` (and subclasses) when
    minimum and/or maximum length requirements are specified and the input string does not match those requirements.

    May contain the extra fields `min_length` and `max_length`, depending on whether they are specified.
    """
    # Placeholder, will be overridden by the subclasses
    code = 'string_invalid_length'

    def __init__(self, *, min_length: Optional[int] = None, max_length: Optional[int] = None, **kwargs: Any):
        if min_length is not None:
            kwargs.update(min_length=min_length)
        if max_length is not None:
            kwargs.update(max_length=max_length)
        super().__init__(**kwargs)


class StringTooShortError(StringInvalidLengthError):
    """
    Validation error raised by `StringValidator` (and subclasses) when a minimum length requirement is specified and the
    input string is too short.

    Contains the extra fields `min_length` and optionally `max_length` (if specified in `StringValidator` as well).
    """
    code = 'string_too_short'

    def __init__(self, *, min_length: int, max_length: Optional[int] = None, **kwargs: Any):
        super().__init__(min_length=min_length, max_length=max_length, **kwargs)


class StringTooLongError(StringInvalidLengthError):
    """
    Validation error raised by `StringValidator` (and subclasses) when a maximum length requirement is specified and the
    input string is too long.

    Contains the extra fields `max_length` and optionally `min_length` (if specified in `StringValidator` as well).
    """
    code = 'string_too_long'

    def __init__(self, *, min_length: Optional[int] = None, max_length: int, **kwargs: Any):
        super().__init__(min_length=min_length, max_length=max_length, **kwargs)


class StringInvalidCharactersError(ValidationError):
    """
    Validation error raised by `StringValidator` (and subclasses) when the input string contains characters that are not
    allowed, e.g. newlines (unless multiline strings are allowed) or other non-printable characters (unless unsafe mode
    is used).
    """
    code = 'string_invalid_characters'
