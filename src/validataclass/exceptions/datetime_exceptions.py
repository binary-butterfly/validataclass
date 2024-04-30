"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

from .base_exceptions import ValidationError

__all__ = [
    'InvalidDateError',
    'InvalidTimeError',
    'InvalidDateTimeError',
    'DateTimeRangeError',
]


class InvalidDateError(ValidationError):
    """
    Validation error raised by `DateValidator` when the input string is not a valid date (in `YYYY-MM-DD` format).

    The extra field `date_format` contains a string with the format that the validator accepts (currently, the format
    is always `YYYY-MM-DD`).
    """
    code = 'invalid_date'

    def __init__(self, **kwargs: Any):
        super().__init__(date_format='YYYY-MM-DD', **kwargs)


class InvalidTimeError(ValidationError):
    """
    Validation error raised by `TimeValidator` when the input string is not a valid time (in `HH:MM` and/or `HH:MM:SS`
    format).

    The extra field `time_format` contains a string with the format that the validator accepts (e.g. `HH:MM`,
    `HH:MM:SS` or `HH:MM[:SS]`).
    """
    code = 'invalid_time'

    def __init__(self, *, time_format_str: str, **kwargs: Any):
        super().__init__(time_format=time_format_str, **kwargs)


class InvalidDateTimeError(ValidationError):
    """
    Validation error raised by `DateTimeValidator` when the input string is not a valid datetime in the format specified
    by the validator.

    The extra field `datetime_format` contains a string representing the format accepted by the validator, with
    placeholders like `<TIME>` (e.g. `<DATE>T<TIME>[<TIMEZONE>]` (literal `T`, timezone is optional) or `<DATE>T<TIME>Z`
    (literal `Z` meaning UTC, although `+00:00` is also allowed).

    The placeholders have the usual formats:

    - `<TIME>` for a time in the format `HH:MM:SS[.fff]` (optionally with milli-/microseconds)
    - `<DATE>` for a date in the format `YYYY-MM-DD`
    - `<TIMEZONE>` for the offset to UTC in the format `+HH:MM`, `-HH:MM` or a literal `Z` for UTC (same as `+00:00`)
    """
    code = 'invalid_datetime'

    def __init__(self, *, datetime_format_str: str, **kwargs: Any):
        super().__init__(datetime_format=datetime_format_str, **kwargs)


class DateTimeRangeError(ValidationError):
    """
    Validation error raised by `DateTimeValidator` when a datetime range (see `DateTimeRange` or `DateTimeOffsetRange`)
    is specified and the input datetime is outside of that range.

    May contain extra fields like `lower_boundary` and `upper_boundary` as returned by the `to_dict()` method of the
    datetime range.
    """
    code = 'datetime_range_error'
