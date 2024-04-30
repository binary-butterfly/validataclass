"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import re
from datetime import time

import pytest

from tests.test_utils import UNSET_PARAMETER
from validataclass.exceptions import InvalidTimeError, InvalidTypeError, RequiredValueError
from validataclass.validators import TimeFormat, TimeValidator


class TimeValidatorTest:
    """
    Unit tests for the TimeValidator.
    """

    # General tests

    @staticmethod
    def test_invalid_none():
        """ Check that TimeValidator raises exceptions for None as value. """
        validator = TimeValidator()

        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)

        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        """ Check that TimeValidator raises exceptions for values that are not of type 'str'. """
        validator = TimeValidator()

        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)

        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_string',
        [
            # Nonsense strings
            '',
            'banana',
            'aa:bb:cc',
            '000000',
            '-01:00:00',
            '00:-01:00',

            # Invalid format
            '12:34:56.123456',
            '12:34:56+01:00',
            '12:34:56:12',

            # Invalid hour/month/second components
            '24:00',
            '24:00:00',
            '00:60',
            '00:60:00',
            '00:00:60',
            '99:99',
            '99:99:99',
        ],
    )
    @pytest.mark.parametrize(
        'time_format, time_format_str',
        [
            # Default format (no format specified in constructor)
            (UNSET_PARAMETER, 'HH:MM:SS'),

            # Explicit format
            (TimeFormat.NO_SECONDS, 'HH:MM'),
            (TimeFormat.WITH_SECONDS, 'HH:MM:SS'),
            (TimeFormat.OPTIONAL_SECONDS, 'HH:MM[:SS]'),
        ],
    )
    def test_all_formats_invalid(input_string, time_format, time_format_str):
        """ Test TimeValidator with all time formats with input that is always invalid. """
        params = {} if time_format is UNSET_PARAMETER else {'time_format': time_format}
        validator = TimeValidator(**params)

        with pytest.raises(InvalidTimeError) as exception_info:
            validator.validate(input_string)

        assert exception_info.value.to_dict() == {
            'code': 'invalid_time',
            'time_format': time_format_str,
        }

    # Test TimeValidator with different time formats

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, expected_time',
        [
            ('00:00', time(0, 0, 0)),
            ('00:59', time(0, 59, 0)),
            ('12:34', time(12, 34, 0)),
            ('13:37', time(13, 37, 0)),
            ('23:59', time(23, 59, 0)),
        ],
    )
    @pytest.mark.parametrize(
        'time_format',
        [
            TimeFormat.NO_SECONDS,
            TimeFormat.OPTIONAL_SECONDS,
        ],
    )
    def test_time_format_hh_mm_valid(input_string, expected_time, time_format):
        """
        Test TimeValidator with "HH:MM" strings (times without seconds) with format settings that allow this
        (NO_SECONDS and OPTIONAL_SECONDS).
        """
        validator = TimeValidator(time_format=time_format)
        validated_time = validator.validate(input_string)

        assert type(validated_time) is time
        assert validated_time == expected_time

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, expected_time',
        [
            ('00:00:00', time(0, 0, 0)),
            ('00:59:59', time(0, 59, 59)),
            ('12:34:56', time(12, 34, 56)),
            ('13:37:00', time(13, 37, 0)),
            ('23:59:59', time(23, 59, 59)),
        ],
    )
    @pytest.mark.parametrize(
        'time_format',
        [
            UNSET_PARAMETER,
            TimeFormat.WITH_SECONDS,
            TimeFormat.OPTIONAL_SECONDS,
        ],
    )
    def test_time_format_hh_mm_ss_valid(input_string, expected_time, time_format):
        """
        Test TimeValidator with "HH:MM:SS" strings (times with seconds) with format settings that allow this (default,
        WITH_SECONDS and OPTIONAL_SECONDS).
        """
        params = {} if time_format is UNSET_PARAMETER else {'time_format': time_format}
        validator = TimeValidator(**params)

        validated_time = validator.validate(input_string)

        assert type(validated_time) is time
        assert validated_time == expected_time

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, time_format, time_format_str',
        [
            # WITH_SECONDS (as default) with HH:MM strings
            ('00:00', UNSET_PARAMETER, 'HH:MM:SS'),
            ('13:37', UNSET_PARAMETER, 'HH:MM:SS'),
            ('23:59', UNSET_PARAMETER, 'HH:MM:SS'),

            # WITH_SECONDS (explicit) with HH:MM strings
            ('00:00', TimeFormat.WITH_SECONDS, 'HH:MM:SS'),
            ('13:37', TimeFormat.WITH_SECONDS, 'HH:MM:SS'),
            ('23:59', TimeFormat.WITH_SECONDS, 'HH:MM:SS'),

            # NO_SECONDS with HH:MM:SS strings
            ('00:00:00', TimeFormat.NO_SECONDS, 'HH:MM'),
            ('12:34:56', TimeFormat.NO_SECONDS, 'HH:MM'),
            ('13:37:00', TimeFormat.NO_SECONDS, 'HH:MM'),
        ],
    )
    def test_with_time_format_invalid(input_string, time_format, time_format_str):
        """ Test TimeValidator with different time formats with invalid input. """
        params = {} if time_format is UNSET_PARAMETER else {'time_format': time_format}
        validator = TimeValidator(**params)

        with pytest.raises(InvalidTimeError) as exception_info:
            validator.validate(input_string)

        assert exception_info.value.to_dict() == {
            'code': 'invalid_time',
            'time_format': time_format_str,
        }

    # Test error handling when time.fromisoformat() raises ValueError

    @staticmethod
    def test_fromisoformat_value_error():
        """ Check that ValueErrors raised by time.fromisoformat() are handled correctly. """
        # As the input is validated by regex before calling time.fromisoformat(), this case should never occur.
        # To test this we need to manipulate the regex to accept invalid strings after creating the validator.
        validator = TimeValidator()
        validator.time_format_regex = re.compile(r'.*')

        with pytest.raises(InvalidTimeError) as exception_info:
            validator.validate('bananana')

        assert exception_info.value.to_dict() == {
            'code': 'invalid_time',
            'time_format': 'HH:MM:SS',
        }
