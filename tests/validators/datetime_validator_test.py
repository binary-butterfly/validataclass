# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timedelta, timezone
from dateutil import tz
import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, InvalidDateTimeError, DateTimeRangeError, \
    InvalidValidatorOptionException
from wtfjson.helpers import DateTimeRange
from wtfjson.validators import DateTimeValidator, DateTimeValidatorFormat


class DateTimeValidatorTest:
    # General tests

    @staticmethod
    def test_invalid_none():
        """ Check that DateTimeValidator raises exceptions for None as value. """
        validator = DateTimeValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        """ Check that DateTimeValidator raises exceptions for values that are not of type 'str'. """
        validator = DateTimeValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # Nonsense strings
            '', 'banana', 'xxxx-xx-xxTxx:xx:xx',
            # Invalid formats
            '20210901T171029', '2021-09-01', '17:10:00',
            # Invalid datetime components
            '2021-13-01T00:00:00', '2021-01-32T00:00:00', '2021-01-01T99:99:99', '2021-01-01T00:00:00A',
            # Timezones with seconds/microseconds (not allowed here)
            '2021-01-01T00:00:00+01:02:03', '2021-01-01T00:00:00+01:02:03.123456',
        ]
    )
    @pytest.mark.parametrize('datetime_format', list(DateTimeValidatorFormat))
    def test_all_formats_invalid(input_string, datetime_format):
        """ Test DateTimeValidator with all datetime formats with input that is always invalid. """
        validator = DateTimeValidator(datetime_format=datetime_format)
        with pytest.raises(InvalidDateTimeError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_datetime',
            'datetime_format': datetime_format.format_str,
        }

    @staticmethod
    def test_default_format_correct():
        """ Check that DateTimeValidator uses the correct default format when none is specified. """
        validator = DateTimeValidator()
        assert validator.datetime_format is DateTimeValidatorFormat.ALLOW_TIMEZONE
        assert validator.datetime_format_regex.pattern == DateTimeValidatorFormat.ALLOW_TIMEZONE.regex_str

    # Test DateTimeValidator with valid data in different formats

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, expected_datetime', [
            ('0001-01-01T00:00:00-01:00', datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=-1)))),
            ('2021-09-01T12:34:56+01:00', datetime(2021, 9, 1, 12, 34, 56, tzinfo=timezone(timedelta(hours=1)))),
            ('2021-09-01T12:34:56-01:00', datetime(2021, 9, 1, 12, 34, 56, tzinfo=timezone(timedelta(hours=-1)))),
            ('2021-09-01T12:34:56.789+02:00', datetime(2021, 9, 1, 12, 34, 56, 789000, tzinfo=timezone(timedelta(hours=2)))),
            ('2021-09-01T12:34:56.789123-02:00', datetime(2021, 9, 1, 12, 34, 56, 789123, tzinfo=timezone(timedelta(hours=-2)))),
            ('2021-12-13T01:02:03+11:30', datetime(2021, 12, 13, 1, 2, 3, tzinfo=timezone(timedelta(minutes=690)))),
            ('2021-12-13T01:02:03-11:30', datetime(2021, 12, 13, 1, 2, 3, tzinfo=timezone(timedelta(minutes=-690)))),
            ('2021-12-13T01:02:03+00:01', datetime(2021, 12, 13, 1, 2, 3, tzinfo=timezone(timedelta(minutes=1)))),
        ]
    )
    @pytest.mark.parametrize(
        'datetime_format', [
            DateTimeValidatorFormat.ALLOW_TIMEZONE,
            DateTimeValidatorFormat.REQUIRE_TIMEZONE,
        ]
    )
    def test_datetime_with_timezone_valid(input_string, expected_datetime, datetime_format):
        """ Test DateTimeValidator with datetime strings that specify arbitrary timezones with formats that allow this. """
        validator = DateTimeValidator(datetime_format=datetime_format)
        validated_datetime = validator.validate(input_string)
        assert type(validated_datetime) is datetime
        assert validated_datetime == expected_datetime

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, expected_datetime', [
            ('0001-01-01T00:00:00Z', datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
            ('0001-01-01T00:00:00+00:00', datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
            ('2021-09-01T12:34:56Z', datetime(2021, 9, 1, 12, 34, 56, tzinfo=timezone.utc)),
            ('2021-09-01T12:34:56+00:00', datetime(2021, 9, 1, 12, 34, 56, tzinfo=timezone.utc)),
            ('2021-09-01T12:34:56.789Z', datetime(2021, 9, 1, 12, 34, 56, 789000, tzinfo=timezone.utc)),
            ('2021-09-01T12:34:56.789+00:00', datetime(2021, 9, 1, 12, 34, 56, 789000, tzinfo=timezone.utc)),
            ('2021-09-01T12:34:56.789123Z', datetime(2021, 9, 1, 12, 34, 56, 789123, tzinfo=timezone.utc)),
            ('2021-09-01T12:34:56.789123+00:00', datetime(2021, 9, 1, 12, 34, 56, 789123, tzinfo=timezone.utc)),
        ]
    )
    @pytest.mark.parametrize(
        'datetime_format', [
            DateTimeValidatorFormat.ALLOW_TIMEZONE,
            DateTimeValidatorFormat.REQUIRE_TIMEZONE,
            DateTimeValidatorFormat.REQUIRE_UTC,
            DateTimeValidatorFormat.LOCAL_OR_UTC,
        ]
    )
    def test_datetime_with_explicit_utc_valid(input_string, expected_datetime, datetime_format):
        """ Test DateTimeValidator with datetime strings that explicitly specify UTC (as Z or +00:00) with formats that allow this. """
        validator = DateTimeValidator(datetime_format=datetime_format)
        validated_datetime = validator.validate(input_string)
        assert type(validated_datetime) is datetime
        assert validated_datetime == expected_datetime
        assert validated_datetime.tzinfo is timezone.utc

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, expected_datetime', [
            ('0001-01-01T00:00:00', datetime(1, 1, 1, 0, 0, 0)),
            ('1970-01-01T01:23:45', datetime(1970, 1, 1, 1, 23, 45)),
            ('2021-09-01T12:34:56', datetime(2021, 9, 1, 12, 34, 56)),
            ('2021-09-01T12:34:56.789', datetime(2021, 9, 1, 12, 34, 56, 789000)),
            ('2021-09-01T12:34:56.789123', datetime(2021, 9, 1, 12, 34, 56, 789123)),
            ('2999-12-31T23:59:59.999999', datetime(2999, 12, 31, 23, 59, 59, 999999)),
        ]
    )
    @pytest.mark.parametrize(
        'datetime_format', [
            DateTimeValidatorFormat.ALLOW_TIMEZONE,
            DateTimeValidatorFormat.LOCAL_ONLY,
            DateTimeValidatorFormat.LOCAL_OR_UTC,
        ]
    )
    def test_datetime_without_timezone_valid(input_string, expected_datetime, datetime_format):
        """ Test DateTimeValidator with datetime strings that do not specify a timezone with formats that allow this. """
        validator = DateTimeValidator(datetime_format=datetime_format)
        validated_datetime = validator.validate(input_string)
        assert type(validated_datetime) is datetime
        assert validated_datetime == expected_datetime
        assert validated_datetime.tzinfo is None

    # Test DateTimeValidator with strings that are invalid for specified formats

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            '2021-09-01T12:34:56+01:00',
            '2021-09-01T12:34:56.789123-02:00',
            '2021-12-13T01:02:03+12:00',
            '2021-12-13T01:02:03-00:01',
        ]
    )
    @pytest.mark.parametrize(
        'datetime_format, datetime_format_str', [
            (DateTimeValidatorFormat.REQUIRE_UTC, '<DATE>T<TIME>Z'),
            (DateTimeValidatorFormat.LOCAL_ONLY, '<DATE>T<TIME>'),
            (DateTimeValidatorFormat.LOCAL_OR_UTC, '<DATE>T<TIME>[Z]'),
        ]
    )
    def test_datetime_with_timezone_invalid(input_string, datetime_format, datetime_format_str):
        """ Test DateTimeValidator with datetime strings that specify arbitrary timezones with formats that do not allow this. """
        validator = DateTimeValidator(datetime_format=datetime_format)
        with pytest.raises(InvalidDateTimeError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_datetime',
            'datetime_format': datetime_format_str,
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            '2021-09-01T12:34:56Z',
            '2021-09-01T12:34:56+00:00',
            '2021-09-01T12:34:56.789Z',
            '2021-09-01T12:34:56.789123Z',
            '2021-09-01T12:34:56.789123+00:00',
        ]
    )
    @pytest.mark.parametrize(
        'datetime_format, datetime_format_str', [
            (DateTimeValidatorFormat.LOCAL_ONLY, '<DATE>T<TIME>'),
        ]
    )
    def test_datetime_with_explicit_utc_invalid(input_string, datetime_format, datetime_format_str):
        """ Test DateTimeValidator with datetime strings that explicitly specify UTC with formats that do not allow any timezone info. """
        validator = DateTimeValidator(datetime_format=datetime_format)
        with pytest.raises(InvalidDateTimeError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_datetime',
            'datetime_format': datetime_format_str,
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            '2021-09-01T12:34:56',
            '2021-09-01T12:34:56.789',
            '2021-09-01T12:34:56.789123',
        ]
    )
    @pytest.mark.parametrize(
        'datetime_format, datetime_format_str', [
            (DateTimeValidatorFormat.REQUIRE_TIMEZONE, '<DATE>T<TIME><TIMEZONE>'),
            (DateTimeValidatorFormat.REQUIRE_UTC, '<DATE>T<TIME>Z'),
        ]
    )
    def test_datetime_without_timezone_invalid(input_string, datetime_format, datetime_format_str):
        """ Test DateTimeValidator with datetime strings that do not specify a timezone with formats that require a timezone info. """
        validator = DateTimeValidator(datetime_format=datetime_format)
        with pytest.raises(InvalidDateTimeError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_datetime',
            'datetime_format': datetime_format_str,
        }

    # Test DateTimeValidator with local_timezone parameter

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, local_timezone, expected_datetime', [
            # Default: local_timezone=None
            ('2021-09-01T12:34:56', None, datetime(2021, 9, 1, 12, 34, 56)),
            ('2021-09-01T12:34:56Z', None, datetime(2021, 9, 1, 12, 34, 56, tzinfo=timezone.utc)),
            ('2021-09-01T12:34:56-03:00', None, datetime(2021, 9, 1, 12, 34, 56, tzinfo=timezone(timedelta(hours=-3)))),

            # Set local_timezone to UTC
            ('2021-09-01T12:34:56', timezone.utc, datetime(2021, 9, 1, 12, 34, 56, tzinfo=timezone.utc)),
            ('2021-09-01T12:34:56Z', timezone.utc, datetime(2021, 9, 1, 12, 34, 56, tzinfo=timezone.utc)),
            ('2021-09-01T12:34:56-03:00', timezone.utc, datetime(2021, 9, 1, 12, 34, 56, tzinfo=timezone(timedelta(hours=-3)))),

            # Test with a timezone that has Daylight Saving Time
            ('2021-02-01T01:02:03', tz.gettz('Europe/Berlin'), datetime(2021, 2, 1, 1, 2, 3, tzinfo=timezone(timedelta(hours=1)))),
            ('2021-02-01T01:02:03Z', tz.gettz('Europe/Berlin'), datetime(2021, 2, 1, 1, 2, 3, tzinfo=timezone.utc)),
            ('2021-07-01T01:02:03', tz.gettz('Europe/Berlin'), datetime(2021, 7, 1, 1, 2, 3, tzinfo=timezone(timedelta(hours=2)))),
            ('2021-07-01T01:02:03Z', tz.gettz('Europe/Berlin'), datetime(2021, 7, 1, 1, 2, 3, tzinfo=timezone.utc)),
        ]
    )
    def test_with_local_timezone_valid(input_string, local_timezone, expected_datetime):
        """ Test DateTimeValidator with local_timezone parameter with valid input. """
        validator = DateTimeValidator(local_timezone=local_timezone)
        validated_datetime = validator.validate(input_string)
        assert validated_datetime == expected_datetime
        # Check timezone of datetimes by comparing their offset to UTC
        assert validated_datetime.tzinfo == expected_datetime.tzinfo or \
               validated_datetime.tzinfo.utcoffset(validated_datetime) == expected_datetime.tzinfo.utcoffset(expected_datetime)

    # Test DateTimeValidator with target_timezone parameter

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, target_timezone, expected_datetime', [
            # Convert local datetimes (Europe/Berlin) with and without DST to UTC
            ('2021-02-01T12:34:56', timezone.utc, datetime(2021, 2, 1, 11, 34, 56, tzinfo=timezone.utc)),
            ('2021-07-01T12:34:56', timezone.utc, datetime(2021, 7, 1, 10, 34, 56, tzinfo=timezone.utc)),

            # Convert local datetimes (Europe/Berlin) with and without DST to a different timezone that has DST
            ('2021-02-01T12:34:56', tz.gettz('Europe/Helsinki'), datetime(2021, 2, 1, 13, 34, 56, tzinfo=tz.gettz('Europe/Helsinki'))),
            ('2021-07-01T12:34:56', tz.gettz('Europe/Helsinki'), datetime(2021, 7, 1, 13, 34, 56, tzinfo=tz.gettz('Europe/Helsinki'))),

            # Convert UTC datetimes to a timezone with DST
            ('2021-02-01T12:34:56Z', tz.gettz('Europe/Helsinki'), datetime(2021, 2, 1, 14, 34, 56, tzinfo=tz.gettz('Europe/Helsinki'))),
            ('2021-07-01T12:34:56Z', tz.gettz('Europe/Helsinki'), datetime(2021, 7, 1, 15, 34, 56, tzinfo=tz.gettz('Europe/Helsinki'))),

            # Convert datetimes with timezone info to UTC
            ('2021-02-01T12:34:56+02:00', timezone.utc, datetime(2021, 2, 1, 10, 34, 56, tzinfo=timezone.utc)),
            ('2021-07-01T12:34:56-05:00', timezone.utc, datetime(2021, 7, 1, 17, 34, 56, tzinfo=timezone.utc)),

            # Convert datetimes with timezone info to a timezone with DST
            ('2021-02-01T00:34:56-12:00', tz.gettz('Europe/Berlin'), datetime(2021, 2, 1, 13, 34, 56, tzinfo=tz.gettz('Europe/Berlin'))),
            ('2021-07-01T00:34:56-12:00', tz.gettz('Europe/Berlin'), datetime(2021, 7, 1, 14, 34, 56, tzinfo=tz.gettz('Europe/Berlin'))),
        ]
    )
    def test_with_target_timezone_valid(input_string, target_timezone, expected_datetime):
        """ Test DateTimeValidator with target_timezone parameter with valid input. """
        validator = DateTimeValidator(local_timezone=tz.gettz('Europe/Berlin'), target_timezone=target_timezone)
        validated_datetime = validator.validate(input_string)
        assert validated_datetime == expected_datetime
        assert validated_datetime.tzinfo is target_timezone

    # Test DateTimeValidator with datetime_range parameter

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, expected_datetime', [
            # Input in UTC
            ('2021-09-08T12:00:00Z', datetime(2021, 9, 8, 12, 0, 0, tzinfo=timezone.utc)),
            ('2021-09-08T12:59:59.999999Z', datetime(2021, 9, 8, 12, 59, 59, 999999, tzinfo=timezone.utc)),
            ('2021-09-08T13:00:00Z', datetime(2021, 9, 8, 13, 0, 0, tzinfo=timezone.utc)),
            # Input in other timezones
            ('2021-09-08T11:00:00-01:00', datetime(2021, 9, 8, 11, 0, 0, tzinfo=timezone(timedelta(hours=-1)))),
            ('2021-09-08T15:00:00+02:00', datetime(2021, 9, 8, 15, 0, 0, tzinfo=timezone(timedelta(hours=2)))),
        ]
    )
    def test_datetime_range_valid(input_string, expected_datetime):
        """ Test DateTimeValidator with datetime_range parameter without local_timezone, with valid input. """
        dt_range = DateTimeRange(lower_boundary=datetime(2021, 9, 8, 12, 0, 0, tzinfo=timezone.utc),
                                 upper_boundary=datetime(2021, 9, 8, 13, 0, 0, tzinfo=timezone.utc))
        validator = DateTimeValidator(DateTimeValidatorFormat.REQUIRE_TIMEZONE, datetime_range=dt_range)
        assert validator.validate(input_string) == expected_datetime

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # Input in UTC
            '2021-09-08T11:59:59.999999Z',
            '2021-09-08T13:00:00.000001Z',
            '2021-09-09T12:30:00Z',
            # Input in other timezones
            '2021-09-08T10:59:59-01:00',
            '2021-09-08T15:00:01+02:00',
        ]
    )
    def test_datetime_range_invalid(input_string):
        """ Test DateTimeValidator with datetime_range parameter without local_timezone, with valid input. """
        dt_range = DateTimeRange(lower_boundary=datetime(2021, 9, 8, 12, 0, 0, tzinfo=timezone.utc),
                                 upper_boundary=datetime(2021, 9, 8, 13, 0, 0, tzinfo=timezone.utc))
        validator = DateTimeValidator(DateTimeValidatorFormat.REQUIRE_TIMEZONE, datetime_range=dt_range)
        with pytest.raises(DateTimeRangeError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'datetime_range_error',
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, expected_datetime', [
            # Input in local timezone (Europe/Berlin with DST, UTC+2)
            ('2021-09-08T14:00:00', datetime(2021, 9, 8, 14, 0, 0, tzinfo=timezone(timedelta(hours=2)))),
            ('2021-09-08T14:30:00', datetime(2021, 9, 8, 14, 30, 0, tzinfo=timezone(timedelta(hours=2)))),
            ('2021-09-08T15:00:00', datetime(2021, 9, 8, 15, 0, 0, tzinfo=timezone(timedelta(hours=2)))),
            # Input in UTC and other timezones
            ('2021-09-08T12:00:00Z', datetime(2021, 9, 8, 12, 0, 0, tzinfo=timezone.utc)),
            ('2021-09-08T13:00:00Z', datetime(2021, 9, 8, 13, 0, 0, tzinfo=timezone.utc)),
            ('2021-09-08T11:00:00-01:00', datetime(2021, 9, 8, 11, 0, 0, tzinfo=timezone(timedelta(hours=-1)))),
            ('2021-09-08T15:00:00+02:00', datetime(2021, 9, 8, 15, 0, 0, tzinfo=timezone(timedelta(hours=2)))),
        ]
    )
    def test_datetime_range_with_local_timezone_valid(input_string, expected_datetime):
        """ Test DateTimeValidator with datetime_range parameter without local_timezone, with valid input. """
        dt_range = DateTimeRange(lower_boundary=datetime(2021, 9, 8, 14, 0, 0),
                                 upper_boundary=datetime(2021, 9, 8, 15, 0, 0))
        validator = DateTimeValidator(local_timezone=tz.gettz('Europe/Berlin'), datetime_range=dt_range)
        assert validator.validate(input_string) == expected_datetime

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # Input in local timezone (Europe/Berlin with DST, UTC+2)
            '2021-09-08T13:59:59',
            '2021-09-08T15:00:01',
            # Input in UTC and other timezones
            '2021-09-08T11:59:59Z',
            '2021-09-08T13:00:01Z',
            '2021-09-08T10:59:59-01:00',
            '2021-09-08T15:00:01+02:00',
        ]
    )
    def test_datetime_range_with_local_timezone_invalid(input_string):
        """ Test DateTimeValidator with datetime_range parameter without local_timezone, with valid input. """
        dt_range = DateTimeRange(lower_boundary=datetime(2021, 9, 8, 14, 0, 0),
                                 upper_boundary=datetime(2021, 9, 8, 15, 0, 0))
        validator = DateTimeValidator(local_timezone=tz.gettz('Europe/Berlin'), datetime_range=dt_range)
        with pytest.raises(DateTimeRangeError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'datetime_range_error',
        }

    # Invalid validator parameters

    @staticmethod
    @pytest.mark.parametrize(
        'datetime_format', [
            DateTimeValidatorFormat.ALLOW_TIMEZONE,
            DateTimeValidatorFormat.LOCAL_OR_UTC,
            DateTimeValidatorFormat.LOCAL_ONLY,
        ]
    )
    def test_invalid_parameter_target_timezone_without_local_timezone(datetime_format):
        """
        Check that DateTimeValidator raises an exception when target_timezone is specified without local_timezone and with a format that
        allows local datetimes.
        """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DateTimeValidator(datetime_format=datetime_format, target_timezone=timezone.utc)
        assert str(exception_info.value) == 'Parameter "local_timezone" is required when a datetime format that allows local datetimes ' \
                                            'is used and "target_timezone" is specified.'
