"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import re
from datetime import datetime, tzinfo
from enum import Enum
from typing import Any, Optional

from validataclass.exceptions import DateTimeRangeError, InvalidDateTimeError, InvalidValidatorOptionException
from validataclass.helpers import BaseDateTimeRange
from .string_validator import StringValidator

__all__ = [
    'DateTimeFormat',
    'DateTimeValidator',
]

# Helper variables to construct more complex regex patterns
_REGEX_DATE = r'(\d{4}-\d{2}-\d{2})'
_REGEX_TIME = r'(\d{2}:\d{2}:\d{2})(\.\d+)?'
_REGEX_TIMEZONE = r'(Z|[+-]\d{2}:\d{2})'
_REGEX_UTC_ONLY = r'(Z|[+-]00:00)'
_REGEX_DATE_AND_TIME = f'{_REGEX_DATE}T{_REGEX_TIME}'


class DateTimeFormat(Enum):
    """
    Enum to specify allowed datetime format (e.g. with/without timezone info).

    Enum members have two properties:

    - `format_str`: String representation used in `InvalidDateTimeError` (e.g. `<DATE>T<TIME>[<TIMEZONE>]`)
    - `regex_str`: Regular expression pattern as string
    """

    def __init__(self, format_str: str, regex_str: str):
        self.format_str = format_str
        self.regex_str = regex_str

    def allows_local(self) -> bool:
        """
        Returns `True` if the format allows local datetimes (i.e. datetime strings without timezone info).
        """
        return bool(self in [
            DateTimeFormat.ALLOW_TIMEZONE,
            DateTimeFormat.LOCAL_ONLY,
            DateTimeFormat.LOCAL_OR_UTC,
        ])

    # Allows datetimes both with and without timezone info, the latter being interpreted as local time (default)
    ALLOW_TIMEZONE = ('<DATE>T<TIME>[<TIMEZONE>]', f'{_REGEX_DATE_AND_TIME}{_REGEX_TIMEZONE}?')

    # Only allows datetimes with timezone info ('Z' suffix for UTC or any '[+-]HH:MM...' timezone)
    REQUIRE_TIMEZONE = ('<DATE>T<TIME><TIMEZONE>', f'{_REGEX_DATE_AND_TIME}{_REGEX_TIMEZONE}')

    # Only allows datetimes in UTC with explicit timezone info ('Z' or '+00:00' suffix)
    REQUIRE_UTC = ('<DATE>T<TIME>Z', f'{_REGEX_DATE_AND_TIME}{_REGEX_UTC_ONLY}')

    # Only allows datetimes without timezone info (will be interpreted as local time)
    LOCAL_ONLY = ('<DATE>T<TIME>', f'{_REGEX_DATE_AND_TIME}')

    # Allows datetimes without timezone info and datetimes in UTC ('Z' or '+00:00'), but no other timezones
    LOCAL_OR_UTC = ('<DATE>T<TIME>[Z]', f'{_REGEX_DATE_AND_TIME}{_REGEX_UTC_ONLY}?')


class DateTimeValidator(StringValidator):
    """
    Validator that parses datetime strings in the ISO 8601 compatible format `YYYY-MM-DDTHH:MM:SS[.fff][+HH:MM]` to
    `datetime.datetime` objects, where `T` stands for the literal character as a separator between date and time (e.g.
    `2021-12-31T12:34:56` or `2021-12-31T12:34:56.123456`) and `.fff` is an arbitrary number of decimal places.

    The string may specify a timezone using `+HH:MM` or `-HH:MM`. Also, the special suffix `Z` is allowed to denote UTC
    as the timezone (e.g. `2021-12-31T12:34:56Z` which is equivalent to `2021-12-31T12:34:56+00:00`). If no timezone is
    specified, the datetime is interpreted as local time (see also the parameter `local_timezone`).

    By default, the validator allows datetimes with and without timezones. To restrict this to specific formats you can
    use the `DateTimeFormat` enum, which has the following values:

    - `ALLOW_TIMEZONE`: Default behavior, allows datetimes with any timezone or without a timezone (local time)
    - `REQUIRE_TIMEZONE`: Only allows datetimes that specify a timezone (but any timezone is allowed)
    - `REQUIRE_UTC`: Only allows datetimes that explicitly specify UTC as timezone (either with `Z` or `+00:00`)
    - `LOCAL_ONLY`: Only allows datetimes **without** timezone (will be interpreted as local time)
    - `LOCAL_OR_UTC`: Only allows local datetimes (no timezone) or UTC datetimes (explicit `Z` or `+00:00`)

    ```
    | Example input             | ALLOW_TIMEZONE | REQUIRE_TIMEZONE | REQUIRE_UTC | LOCAL_ONLY | LOCAL_OR_UTC |
    |---------------------------|----------------|------------------|-------------|------------|--------------|
    | 2021-12-31T12:34:56       | valid          |                  |             | valid      | valid        |
    | 2021-12-31T12:34:56Z      | valid          | valid            | valid       |            | valid        |
    | 2021-12-31T12:34:56+00:00 | valid          | valid            | valid       |            | valid        |
    | 2021-12-31T12:34:56+02:00 | valid          | valid            |             |            |              |
    ```

    The validator always accepts input strings with milli- and microseconds (e.g. `2021-12-31T12:34:56.123` or
    `2021-12-31T12:34:56.123456`). It also accepts higher precisions (i.e. nanoseconds and beyond), but anything smaller
    than microseconds will be discarded, since `datetime` doesn't support it (so `2021-12-31T12:34:56.123456789` will be
    interpreted as `2021-12-31T12:34:56.123456`).

    You can set the option `discard_milliseconds=True`, which will discard the milli- and microseconds of the output
    datetime (all of the examples would then result in the same datetime as `2021-12-31T12:34:56`).

    The parameter `local_timezone` can be used to set the timezone for datetime strings that don't specify a timezone.
    For example, if `local_timezone` is set to a UTC+3 timezone, the string `2021-12-31T12:34:56` will be treated like
    `2021-12-31T12:34:56+03:00`. Similarly, to interpret datetimes without timezone as UTC, set
    `local_timezone=datetime.timezone.utc`. By default, if the input datetime does not specify a timezone, the resulting
    datetime will be a naive datetime without any timezone info, i.e. `tzinfo=None`.

    The parameter `target_timezone` can be used to convert all resulting datetime objects to a uniform timezone. This
    requires the datetimes to already have a timezone, though, so if you are using a format that allows local datetimes,
    you need to specify `local_timezone` as well.

    See [`datetime.timezone`](https://docs.python.org/3/library/datetime.html#timezone-objects) and
    [`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html) for information on defining timezones.

    Additionally, the parameter `datetime_range` can be used to specify a range of datetime values that are allowed
    (e.g. a minimum and a maximum datetime, which can be dynamically defined using callables). See the classes
    `DateTimeRange` and `DateTimeOffsetRange` from `validataclass.helpers` for further information.

    **Note:** When using datetime ranges, make sure not to mix datetimes that have timezones with local datetimes
    because those comparisons will raise `TypeError` exceptions. It's recommended either to use only datetimes with
    defined timezones (for both input values and the boundaries of the datetime ranges), or to specify the
    `local_timezone` parameter (which will also be used to determine the timezone of the range boundary datetimes if
    they do not specify timezones themselves).

    **Examples:**

    ```
    # Use `timezone.utc` from `datetime` to specify UTC as timezone
    from datetime import timezone
    # Use `zoneinfo.ZoneInfo` to easily specify timezones that are not UTC
    from zoneinfo import ZoneInfo

    from validataclass.validators import DateTimeValidator, DateTimeFormat

    # Default format (ALLOW_TIMEZONE): Allow datetimes with and without timezone
    validator = DateTimeValidator()
    validator.validate("2021-12-31T12:34:56")        # -> datetime(2021, 12, 31, 12, 34, 56)
    validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56+02:00")  # -> datetime(2021, 12, 31, 12, 34, 56,
                                                     #             tzinfo=timezone(timedelta(seconds=7200)))
    # Times with milliseconds/microseconds:
    validator.validate("2021-12-31T12:34:56.123")     # -> datetime(2021, 12, 31, 12, 34, 56, 123000)
    validator.validate("2021-12-31T12:34:56.123456")  # -> datetime(2021, 12, 31, 12, 34, 56, 123456)

    # REQUIRE_TIMEZONE format: Only allow datetimes with specified timezone
    validator = DateTimeValidator(DateTimeFormat.REQUIRE_TIMEZONE)
    validator.validate("2021-12-31T12:34:56")        # raises InvalidDateTimeError
    validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56+02:00")  # -> datetime(2021, 12, 31, 12, 34, 56,
                                                     #             tzinfo=timezone(timedelta(seconds=7200)))

    # LOCAL_OR_UTC format: Only allow datetimes either without timezone or with UTC explicitly specified
    validator = DateTimeValidator(DateTimeFormat.LOCAL_OR_UTC)
    validator.validate("2021-12-31T12:34:56")        # -> datetime(2021, 12, 31, 12, 34, 56)
    validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56+00:00")  # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56+02:00")  # raises InvalidDateTimeError

    # LOCAL_OR_UTC, but with a specified local timezone (as default value for the datetime's tzinfo)
    validator = DateTimeValidator(DateTimeFormat.LOCAL_OR_UTC, local_timezone=ZoneInfo('Europe/Berlin'))
    validator.validate("2021-12-31T12:34:56")        # -> datetime(2021, 12, 31, 12, 34, 56,
                                                     #             tzinfo=zoneinfo.ZoneInfo(key='Europe/Berlin'))
    validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56+00:00")  # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56+02:00")  # raises InvalidDateTimeError

    # Allow datetimes with arbitrary timezones (using CET/CEST (+01:00/+02:00) as local timezone), but convert all
    # datetimes to UTC
    validator = DateTimeValidator(local_timezone=ZoneInfo('Europe/Berlin'), target_timezone=timezone.utc)
    validator.validate("2021-12-31T12:34:56")        # -> datetime(2021, 12, 31, 11, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56+00:00")  # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56+02:00")  # -> datetime(2021, 12, 31, 10, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T12:34:56-06:00")  # -> datetime(2021, 12, 31, 18, 34, 56, tzinfo=timezone.utc)
    ```

    **Examples for datetime ranges:**

    ```python
    from datetime import datetime, timedelta, timezone

    from validataclass.helpers import DateTimeRange, DateTimeOffsetRange
    from validataclass.validators import DateTimeValidator, DateTimeFormat

    # DateTimeRange: Only allow datetimes within a specified datetime range, e.g. allow all datetimes in the year 2021
    validator = DateTimeValidator(
        DateTimeFormat.REQUIRE_TIMEZONE,
        target_timezone=timezone.utc,
        datetime_range=DateTimeRange(
            datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            datetime(2021, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc),
        ),
    )

    # Valid datetimes in the specified datetime range
    validator.validate("2021-01-01T00:00:00Z")       # -> datetime(2021, 1, 1, 0, 0, tzinfo=timezone.utc)
    validator.validate("2021-07-28T12:34:56Z")       # -> datetime(2021, 7, 28, 12, 34, 56, tzinfo=timezone.utc)
    validator.validate("2021-12-31T23:59:59Z")       # -> datetime(2021, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    # These appear to be outside of the range, but are inside when taking the timezones into account
    validator.validate("2020-12-31T23:00:00-01:00")  # -> datetime(2021, 1, 1, 0, 0, tzinfo=timezone.utc)
    validator.validate("2022-01-01T00:00:00+01:00")  # -> datetime(2021, 12, 31, 23, 0, tzinfo=timezone.utc)

    # These will all raise a DateTimeRangeError with lower_boundary and upper_boundary set to the datetime range
    validator.validate("2020-12-31T23:59:59Z")       # raises DateTimeRangeError
    validator.validate("2022-01-01T00:00:00Z")       # raises DateTimeRangeError
    validator.validate("2021-01-01T00:00:00+01:00")  # raises DateTimeRangeError
    validator.validate("2021-12-31T23:59:59-01:00")  # raises DateTimeRangeError


    # DateTimeOffsetRange: Specify a datetime range using a pivot datetime and two offsets (allows all datetimes
    # "around" the pivot datetime plus/minus the offsets), e.g. all datetimes between pivot_datetime - 5 minutes and
    # pivot_datetime + 10 minutes:
    validator = DateTimeValidator(
        DateTimeFormat.REQUIRE_UTC,
        datetime_range=DateTimeOffsetRange(
            pivot=datetime(2021, 7, 15, 12, 30, 0, tzinfo=timezone.utc),
            offset_minus=timedelta(minutes=5),
            offset_plus=timedelta(minutes=10),
        ),
    )

    # Valid datetimes in the specified datetime range
    validator.validate("2021-07-15T12:25:00Z")  # -> datetime(2021, 7, 15, 12, 25, tzinfo=timezone.utc)
    validator.validate("2021-07-15T12:30:00Z")  # -> datetime(2021, 7, 15, 12, 30, tzinfo=timezone.utc)
    validator.validate("2021-07-15T12:40:00Z")  # -> datetime(2021, 7, 15, 12, 40, tzinfo=timezone.utc)

    # These will all raise a DateTimeRangeError with lower_boundary='2021-07-15T12:25:00+00:00'
    # and upper_boundary='2021-07-15T12:40:00+00:00'
    validator.validate("2021-07-14T12:30:00Z")  # raises DateTimeRangeError (time fits, but day is out of range)
    validator.validate("2021-07-15T12:24:59Z")  # raises DateTimeRangeError (one second too early)
    validator.validate("2021-07-15T12:40:01Z")  # raises DateTimeRangeError (one second too late)
    ```

    The pivot in a `DateTimeOffsetRange` can also be a callable, which will be evaluated just when the `validate()`
    method is called. If the pivot is undefined, it will default to the current date and time (in UTC and without
    milliseconds) at the point of validation.

    **Example for `DateTimeOffsetRange` with the default pivot:**

    ```python
    from datetime import timedelta

    from validataclass.helpers import DateTimeOffsetRange
    from validataclass.validators import DateTimeValidator, DateTimeFormat

    # This example allows all datetimes in the next 7 days, but no datetimes in the past or after these 7 days:
    validator = DateTimeValidator(
        DateTimeFormat.REQUIRE_UTC,
        datetime_range=DateTimeOffsetRange(offset_plus=timedelta(days=7)),
    )

    # Assuming the current date and time is: 2021-10-12, 12:00:00 UTC
    validator.validate("2021-10-12T12:00:00Z")  # -> datetime(2021, 10, 12, 12, 0, 0, tzinfo=timezone.utc)
    validator.validate("2021-10-15T01:23:45Z")  # -> datetime(2021, 10, 15, 1, 23, 45, tzinfo=timezone.utc)
    validator.validate("2021-10-19T11:59:59Z")  # -> datetime(2021, 10, 19, 11, 59, 59, tzinfo=timezone.utc)

    # These will all raise a DateTimeRangeError with lower_boundary set to the current date and time
    # ('2021-07-15T12:25:00+00:00') and upper_boundary set to 7 days in the future (so '2021-07-15T12:40:00+00:00')
    validator.validate("2021-10-12T11:59:59Z")  # raises DateTimeRangeError (one second in the past)
    validator.validate("2021-10-19T12:00:01Z")  # raises DateTimeRangeError (one second too late)
    validator.validate("2021-10-20T12:00:00Z")  # raises DateTimeRangeError (one day too late)

    # Also, the time is reevaluated everytime validate() is called, so the following call will work after creating the
    # validator, but fail after waiting for at least one second. The boundaries in the DateTimeRangeError will have
    # changed accordingly.
    validator.validate("2021-10-12T12:00:00Z")  # now raises DateTimeRangeError
    ```

    See also: `DateValidator`, `TimeValidator`

    Valid input: Datetime strings in the format specified above as `str`
    Output: `datetime.datetime`
    """

    # Datetime string format (enum)
    datetime_format: DateTimeFormat

    # Precompiled regular expression for the specified datetime string format
    datetime_format_regex: re.Pattern[str]

    # Whether to discard milli- and microseconds in the output datetime
    discard_milliseconds: bool = False

    # Timezone to use for datetime strings without a specified timezone (None: no default timezone info in datetime)
    local_timezone: Optional[tzinfo] = None

    # Target timezone that all datetimes will be converted to (None: no timezone conversion)
    target_timezone: Optional[tzinfo] = None

    # Datetime range that defines which values are allowed
    datetime_range: Optional[BaseDateTimeRange] = None

    def __init__(
        self,
        datetime_format: DateTimeFormat = DateTimeFormat.ALLOW_TIMEZONE,
        *,
        discard_milliseconds: bool = False,
        local_timezone: Optional[tzinfo] = None,
        target_timezone: Optional[tzinfo] = None,
        datetime_range: Optional[BaseDateTimeRange] = None,
    ):
        """
        Creates a `DateTimeValidator` with a specified datetime string format, optionally a local timezone, a target
        timezone and/or a datetime range.

        If a target timezone is specified and a format that allows local datetimes is used (`ALLOW_TIMEZONE`,
        `LOCAL_ONLY` or `LOCAL_OR_UTC`), the parameter `local_timezone` is required (otherwise it would be unclear how
        to interpret and convert local datetimes).

        To define datetime ranges using the `datetime_range` parameter, see the classes `DateTimeRange` and
        `DateTimeOffsetRange` from `validataclass.helpers`.

        Parameters:
            `datetime_format`: `DateTimeFormat`, specifies the accepted string formats (default: `ALLOW_TIMEZONE`)
            `discard_milliseconds`: `bool`, if set, remove milli- and microseconds from the datetime (default: `False`)
            `local_timezone`: `tzinfo`, specifies timezone to set for datetimes without timezone info (default: `None`)
            `target_timezone`: `tzinfo`, convert datetimes to this timezone if specified (default: `None`)
            `datetime_range`: `BaseDateTimeRange` (subclasses), specifies the range of allowed values (default: `None`)
        """
        # Initialize StringValidator without any parameters
        super().__init__()

        # Check parameter validity
        if target_timezone is not None and datetime_format.allows_local() and local_timezone is None:
            raise InvalidValidatorOptionException(
                'Parameter "local_timezone" is required when a datetime format that allows local datetimes is used and '
                '"target_timezone" is specified.'
            )

        # Save parameters
        self.datetime_format = datetime_format
        self.discard_milliseconds = discard_milliseconds
        self.local_timezone = local_timezone
        self.target_timezone = target_timezone
        self.datetime_range = datetime_range

        # Precompile regular expression for datetime format
        self.datetime_format_regex = re.compile(self.datetime_format.regex_str)

    def validate(self, input_data: Any, **kwargs: Any) -> datetime:  # type: ignore[override]
        """
        Validates input as a valid datetime string and convert it to a `datetime.datetime` object.
        """
        # First, validate input data as string
        datetime_string = super().validate(input_data, **kwargs)

        # Validate string format with a regular expression
        valid_input_match = self.datetime_format_regex.fullmatch(datetime_string)
        if not valid_input_match:
            raise InvalidDateTimeError(datetime_format_str=self.datetime_format.format_str)

        # Split the valid input into four groups (for easier modifications)
        if self.datetime_format == DateTimeFormat.LOCAL_ONLY:
            date_string, time_string, milliseconds_string = valid_input_match.groups(default='')
            # Set default value separately because LOCAL_ONLY format does not contain a timezone string
            timezone_string = ''
        else:
            date_string, time_string, milliseconds_string, timezone_string = valid_input_match.groups(default='')

        # Replace 'Z' timezone suffix to make the string compatible with oder versions of fromisoformat()
        # (which only accepts 'Z' timezone since python 3.11)
        if timezone_string == 'Z':
            timezone_string = '+00:00'

        # Fix the length of the milli-/microseconds part to make the string compatible with older versions of
        # fromisoformat() (which only accepts arbitrary precision decimal seconds since python 3.11)
        if milliseconds_string:
            # Pad with zeroes and cut off after 6 decimal places
            milliseconds_string = f'{milliseconds_string}000000'[:7]

        # Put the modified string back together
        datetime_string = f'{date_string}T{time_string}{milliseconds_string}{timezone_string}'

        # Try to create datetime object from string (accepts a certain subset of ISO 8601 datetime strings)
        try:
            datetime_obj = datetime.fromisoformat(datetime_string)
        except ValueError:
            raise InvalidDateTimeError(datetime_format_str=self.datetime_format.format_str)

        # Discard milli- and microseconds (if enabled)
        if self.discard_milliseconds:
            datetime_obj = datetime_obj.replace(microsecond=0)

        # Set timezone to local_timezone if no timezone is specified
        if datetime_obj.tzinfo is None and self.local_timezone is not None:
            datetime_obj = datetime_obj.replace(tzinfo=self.local_timezone)

        # Check datetime against datetime_range (if defined)
        if (
            self.datetime_range is not None
            and not self.datetime_range.contains_datetime(datetime_obj, self.local_timezone)
        ):
            # Add extra fields (lower_boundary, upper_boundary) to the validation error
            raise DateTimeRangeError(**self.datetime_range.to_dict(self.local_timezone))

        # Convert datetime to target timezone (if defined)
        if self.target_timezone is not None:
            datetime_obj = datetime_obj.astimezone(self.target_timezone)

        return datetime_obj
