# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import ValidationError

__all__ = [
    'InvalidDateError',
    'InvalidTimeError',
]


class InvalidDateError(ValidationError):
    """
    Validation error raised by `DateValidator` when the input string is not a valid date (in "YYYY-MM-DD" format).

    The extra field 'date_format' contains a string with the format accepted by the validator (fixed string "YYYY-MM-DD" currently).
    """
    code = 'invalid_date'

    def __init__(self, **kwargs):
        super().__init__(date_format='YYYY-MM-DD', **kwargs)


class InvalidTimeError(ValidationError):
    """
    Validation error raised by `TimeValidator` when the input string is not a valid time (in "HH:MM" and/or "HH:MM:SS" format).

    The extra field 'time_format' contains a string with the format accepted by the validator (e.g. "HH:MM", "HH:MM:SS", "HH:MM[:SS]").
    """
    code = 'invalid_time'

    def __init__(self, *, time_format_str: str, **kwargs):
        super().__init__(time_format=time_format_str, **kwargs)
