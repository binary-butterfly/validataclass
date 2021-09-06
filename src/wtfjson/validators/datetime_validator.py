# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, tzinfo
from enum import Enum
import re
from typing import Any, Optional

from .string_validator import StringValidator
from wtfjson.exceptions import InvalidDateTimeError, InvalidValidatorOptionException

__all__ = [
    'DateTimeValidator',
    'DateTimeValidatorFormat',
]

# Helper variables to construct more complex regex patterns
_REGEX_DATE = r'(\d{4}-\d{2}-\d{2})'
_REGEX_TIME = r'(\d{2}:\d{2}:\d{2}(\.\d{3}(\d{3})?)?)'
_REGEX_TIMEZONE = r'(Z|[+-]\d{2}:\d{2})'
_REGEX_UTC_ONLY = r'(Z|[+-]00:00)'
_REGEX_DATE_AND_TIME = f'{_REGEX_DATE}T{_REGEX_TIME}'


class DateTimeValidatorFormat(Enum):
    """
    Enum to specify allowed datetime format (e.g. with/without timezone info).

    Enum members have two properties:
    - format_str: String representation used in InvalidDateTimeError (e.g. "<DATE>T<TIME>[<TIMEZONE>]")
    - regex_str: Regular expression pattern as string
    """

    def __init__(self, format_str, regex_str):
        self.format_str = format_str
        self.regex_str = regex_str

    def allows_local(self) -> bool:
        """ Returns True if the format allows local datetimes (i.e. datetime strings without timezone info). """
        return True if self in [self.ALLOW_TIMEZONE, self.LOCAL_ONLY, self.LOCAL_OR_UTC] else False

    # Allows datetimes both with and without timezone info, the latter being interpreted as local time (default)
    ALLOW_TIMEZONE = ('<DATE>T<TIME>[<TIMEZONE>]', f'{_REGEX_DATE_AND_TIME}{_REGEX_TIMEZONE}?')

    # Only allows datetimes with timezone info ('Z' suffix for UTC or any '[+-]HH:MM...' timezone)
    REQUIRE_TIMEZONE = ('<DATE>T<TIME><TIMEZONE>', f'{_REGEX_DATE_AND_TIME}{_REGEX_TIMEZONE}')

    # Only allows datetimes in UTC with explicit timezone info ('Z' or '+00:00' suffix)
    REQUIRE_UTC = ('<DATE>T<TIME>Z', f'{_REGEX_DATE_AND_TIME}{_REGEX_UTC_ONLY}')

    # Only allows datetimes without timezone info (will be interpreted as local time)
    LOCAL_ONLY = ('<DATE>T<TIME>', f'{_REGEX_DATE_AND_TIME}')

    # Allows datetimes without timezone info (as local time) and datetimes in UTC ('Z' or '+00:00'), but no other timezones
    LOCAL_OR_UTC = ('<DATE>T<TIME>[Z]', f'{_REGEX_DATE_AND_TIME}{_REGEX_UTC_ONLY}?')


class DateTimeValidator(StringValidator):
    """
    Validator that parses datetime strings in the ISO 8601 compatible format "YYYY-MM-DDTHH:MM:SS[.fff[fff][+HH:MM]" to `datetime.datetime`
    objects, where "T" stands for the literal character as a separator between date and time (e.g. "2021-12-31T12:34:56" or
    "2021-12-31T12:34:56.123456").

    The string may specify a timezone using "+HH:MM" or "-HH:MM". Also the special suffix "Z" is allowed to denote UTC as the timezone
    (e.g. "2021-12-31T12:34:56Z" which is equivalent to "2021-12-31T12:34:56+00:00"). If no timezone is specified, the datetime is
    interpreted as local time (see also the parameter 'local_timezone').

    By default the validator allows datetimes with and without timezones. To restrict this to specific formats you can use the
    `DateTimeValidatorFormat` enum, which has the following values:

    - ALLOW_TIMEZONE: Default behavior, allows datetimes with any timezone or without a timezone (local time)
    - REQUIRE_TIMEZONE: Only allows datetimes that specify a timezone (but any timezone is allowed)
    - REQUIRE_UTC: Only allows datetimes that explicitly specify UTC as timezone (either with "Z" or "+00:00")
    - LOCAL_ONLY: Only allows datetimes WITHOUT timezone (will be interpreted as local time)
    - LOCAL_OR_UTC: Only allows local datetimes (no timezone) or UTC datetimes (explicitly specified with "Z" or "+00:00")

    ```
    Example input             | ALLOW_TIMEZONE | REQUIRE_TIMEZONE | REQUIRE_UTC | LOCAL_ONLY | LOCAL_OR_UTC
    --------------------------|----------------|------------------|-------------|------------|-------------
    2021-12-31T12:34:56       | valid          |                  |             | valid      | valid
    2021-12-31T12:34:56Z      | valid          | valid            | valid       |            | valid
    2021-12-31T12:34:56+00:00 | valid          | valid            | valid       |            | valid
    2021-12-31T12:34:56+02:00 | valid          | valid            |             |            |
    ```

    The parameter 'local_timezone' can be used to set the timezone for datetime strings that don't specify a timezone. For example, if
    'local_timezone' is set to a UTC+3 timezone, the string "2021-12-31T12:34:56" will be treated like "2021-12-31T12:34:56+03:00".
    Similarly, to interpret datetimes without timezone as UTC, set `local_timezone=datetime.timezone.utc`. If 'local_timezone' is not
    set (which is the default), the resulting datetime will have no timezone info (`tzinfo=None`).

    The parameter 'target_timezone' can be used to convert all resulting datetime objects to a uniform timezone. This requires the
    datetimes to already have a timezone, so to allow local datetimes (without timezone info in the input string) you need to specify
    'local_timezone' as well.

    See `datetime.timezone` and `dateutil.tz` (https://dateutil.readthedocs.io/en/stable/tz.html) for information on defining timezones.

    Examples:

    ```
    # Use `dateutil.tz` to easily specify timezones apart from UTC
    from dateutil import tz

    # Validate datetimes with and without timezone
    # "2021-12-31T12:34:56" -> datetime(2021, 12, 31, 12, 34, 56)
    # "2021-12-31T12:34:56+02:00" -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone(timedelta(hours=2)))
    DateTimeValidator()

    # Only allow datetimes with specified timezone
    # "2021-12-31T12:34:56+02:00" -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone(timedelta(hours=2)))
    DateTimeValidator(DateTimeValidatorFormat.REQUIRE_TIMEZONE)

    # Only allow datetimes either without timezone (local time) or with UTC explicitly specified ('Z' or '+00:00' suffix)
    # "2021-12-31T12:34:56" -> datetime(2021, 12, 31, 12, 34, 56)
    # "2021-12-31T12:34:56Z" -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    DateTimeValidator(DateTimeValidatorFormat.LOCAL_OR_UTC)

    # As above (local time or UTC), but set a local_timezone as the default value for the datetime's tzinfo
    # "2021-12-31T12:34:56" -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=tz.gettz('Europe/Berlin'))
    # "2021-12-31T12:34:56Z" -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
    DateTimeValidator(DateTimeValidatorFormat.LOCAL_OR_UTC, local_timezone=tz.gettz('Europe/Berlin'))

    # Allow datetime strings with and without timezone (using CET/CEST (+01:00/+02:00) as default), but convert all datetimes to UTC
    # "2021-12-31T12:34:56" -> datetime(2021, 12, 31, 11, 34, 56, tzinfo=timezone.utc) (input interpreted as UTC+01:00)
    # "2021-12-31T12:34:56Z" -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc) (unchanged because it's already UTC)
    # "2021-12-31T12:34:56-06:00" -> datetime(2021, 12, 31, 18, 34, 56, tzinfo=timezone.utc)
    DateTimeValidator(local_timezone=tz.gettz('Europe/Berlin'), target_timezone=timezone.utc)
    ```

    See also: `DateValidator`, `TimeValidator`

    Valid input: Datetime strings in the format specified above as `str`
    Output: `datetime.datetime`
    """

    # Datetime string format (enum)
    datetime_format: DateTimeValidatorFormat

    # Precompiled regular expression for the specified datetime string format
    datetime_format_regex: re.Pattern

    # Timezone to use for datetime strings without a specified timezone (None: no default timezone info in datetime)
    local_timezone: Optional[tzinfo] = None

    # Target timezone that all datetimes will be converted to (None: no timezone conversion)
    target_timezone: Optional[tzinfo] = None

    # TODO: DateTimeRange

    def __init__(self, datetime_format: DateTimeValidatorFormat = DateTimeValidatorFormat.ALLOW_TIMEZONE, *,
                 local_timezone: Optional[tzinfo] = None, target_timezone: Optional[tzinfo] = None):
        """
        Create a `DateTimeValidator` with a specified datetime string format, optionally a local timezone and/or a target timezone.

        If a target timezone is specified and a format that allows local datetimes is used (ALLOW_TIMEZONE, LOCAL_ONLY or LOCAL_OR_UTC),
        the parameter "local_timezone" is required (otherwise it would be unclear how to interpret and convert local datetimes).

        Parameters:
            datetime_format: `DateTimeValidatorFormat`, specifies the accepted string formats (default: `ALLOW_TIMEZONE`)
            local_timezone: `tzinfo`, specifies the default timezone to set for datetime strings without timezone info (default: None)
            target_timezone: `tzinfo`, if specified, all datetimes will be converted to this timezone (default: None)
        """
        # Initialize StringValidator without any parameters
        super().__init__()

        # Check parameter validity
        if target_timezone is not None and datetime_format.allows_local() and local_timezone is None:
            raise InvalidValidatorOptionException('Parameter "local_timezone" is required when a datetime format that allows local '
                                                  'datetimes is used and "target_timezone" is specified.')

        # Save parameters and precompile regular expression
        self.datetime_format = datetime_format
        self.datetime_format_regex = re.compile(self.datetime_format.regex_str)
        self.local_timezone = local_timezone
        self.target_timezone = target_timezone

    def validate(self, input_data: Any) -> datetime:
        """
        Validate input as a valid datetime string and convert it to a `datetime.datetime` object.
        """
        # First, validate input data as string
        datetime_string = super().validate(input_data)

        # Validate string format with a regular expression
        if not self.datetime_format_regex.fullmatch(datetime_string):
            raise InvalidDateTimeError(datetime_format_str=self.datetime_format.format_str)

        # Replace 'Z' suffix to make the string compatible with fromisoformat()
        if datetime_string[-1] == 'Z':
            datetime_string = datetime_string[:-1] + '+00:00'

        # Try to create datetime object from string (accepts a certain subset of ISO 8601 datetime strings)
        try:
            datetime_obj = datetime.fromisoformat(datetime_string)
        except ValueError:
            raise InvalidDateTimeError(datetime_format_str=self.datetime_format.format_str)

        # Set timezone to local_timezone if no timezone is specified
        if datetime_obj.tzinfo is None and self.local_timezone is not None:
            datetime_obj = datetime_obj.replace(tzinfo=self.local_timezone)

        # Convert datetime to target timezone (if defined)
        if self.target_timezone is not None:
            datetime_obj = datetime_obj.astimezone(self.target_timezone)

        return datetime_obj
