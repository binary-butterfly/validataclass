# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date
from typing import Any

from .string_validator import StringValidator
from wtfjson.exceptions import InvalidDateError

__all__ = [
    'DateValidator',
]


class DateValidator(StringValidator):
    """
    Validator that parses date strings in "YYYY-MM-DD" format (e.g. "2021-01-31") to `datetime.date` objects.

    Currently no parameters are supported.

    Examples:

    ```
    DateValidator()
    ```

    See also: `TimeValidator`, `DateTimeValidator`

    Valid input: Valid dates in YYYY-MM-DD format as `str`
    Output: `datetime.date`
    """

    def __init__(self):
        """
        Create a `DateValidator`. No parameters.
        """
        # Initialize StringValidator without any parameters
        super().__init__()

    def validate(self, input_data: Any) -> date:
        """
        Validate input as a valid date string and convert it to a `datetime.date` object.
        """
        # First, validate input data as string
        date_string = super().validate(input_data)

        # Try to create date object from string (only accepts "YYYY-MM-DD")
        try:
            date_obj = date.fromisoformat(date_string)
        except ValueError:
            raise InvalidDateError()

        return date_obj
