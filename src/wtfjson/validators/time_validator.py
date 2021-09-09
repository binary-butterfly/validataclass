# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import time
from enum import Enum
import re
from typing import Any

from .string_validator import StringValidator
from wtfjson.exceptions import InvalidTimeError

__all__ = [
    'TimeFormat',
    'TimeValidator',
]


class TimeFormat(Enum):
    """
    Enum to specify time string format for `TimeValidator`.

    Enum members have two properties:
    - format_str: String representation used in InvalidTimeError (e.g. "HH:MM[:SS]")
    - regex_str: Regular expression pattern as string
    """

    def __init__(self, format_str, regex_str):
        self.format_str = format_str
        self.regex_str = regex_str

    # Only allows "HH:MM"
    NO_SECONDS = ('HH:MM', r'([01][0-9]|2[0-3]):[0-5][0-9]')

    # Only allows "HH:MM:SS"
    WITH_SECONDS = ('HH:MM:SS', r'([01][0-9]|2[0-3])(:[0-5][0-9]){2}')

    # Allows both "HH:MM:SS" and "HH:MM"
    OPTIONAL_SECONDS = ('HH:MM[:SS]', r'([01][0-9]|2[0-3])(:[0-5][0-9]){1,2}')


class TimeValidator(StringValidator):
    """
    Validator that parses time strings in "HH:MM:SS" or "HH:MM" format (e.g. "13:05:59" / "13:05") to `datetime.time` objects.

    The exact format can be specified using the `TimeFormat` enum, which has the following values:

    - NO_SECONDS: Only allows "HH:MM" strings
    - WITH_SECONDS: Only allows "HH:MM:SS" strings
    - OPTIONAL_SECONDS: Allows both "HH:MM:SS" and "HH:MM" strings (where "HH:MM" is equivalent to "HH:MM:00")

    The default format is `TimeFormat.WITH_SECONDS` ("HH:MM:SS").

    Examples:

    ```
    # Validates "HH:MM:SS" strings (e.g. "13:05:59" -> datetime.time(13, 5, 59), while "13:05" raises an InvalidTimeError)
    TimeValidator()

    # Validates "HH:MM" strings (e.g. "13:05" -> datetime.time(13, 5, 0), while "13:05:59" raises an InvalidTimeError)
    TimeValidator(TimeFormat.NO_SECONDS)

    # Validates both "HH:MM:SS" and "HH:MM" (e.g. "13:05:59" and "13:05" are both valid)
    TimeValidator(TimeFormat.OPTIONAL_SECONDS)
    ```

    See also: `DateValidator`, `DateTimeValidator`

    Valid input: Valid time strings in the specified format
    Output: `datetime.time`
    """

    # Time string format (enum)
    time_format: TimeFormat

    # Precompiled regular expression for the specified time string format
    time_format_regex: re.Pattern

    def __init__(self, time_format: TimeFormat = TimeFormat.WITH_SECONDS):
        """
        Create a `TimeValidator` with a specified time string format.

        Parameters:
            time_format: `TimeFormat`, specifies the accepted string format (default: `TimeFormat.WITH_SECONDS`)
        """
        # Initialize StringValidator without any parameters
        super().__init__()

        # Save time format and precompile regular expression
        self.time_format = time_format
        self.time_format_regex = re.compile(self.time_format.regex_str)

    def validate(self, input_data: Any) -> time:
        """
        Validate input as a valid time string and convert it to a `datetime.time` object.
        """
        # First, validate input data as string
        time_string = super().validate(input_data)

        # Validate string format with a regular expression
        if not self.time_format_regex.fullmatch(time_string):
            raise InvalidTimeError(time_format_str=self.time_format.format_str)

        # Try to create time object from string
        try:
            time_obj = time.fromisoformat(time_string)
        except ValueError:
            raise InvalidTimeError(time_format_str=self.time_format.format_str)

        return time_obj
