# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date
import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, InvalidDateError
from wtfjson.validators import DateValidator


class DateValidatorTest:
    # General tests

    @staticmethod
    def test_invalid_none():
        """ Check that DateValidator raises exceptions for None as value. """
        validator = DateValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        """ Check that DateValidator raises exceptions for values that are not of type 'str'. """
        validator = DateValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    # Test DateValidator with various date strings

    @staticmethod
    @pytest.mark.parametrize(
        'input_string, expected_date', [
            # Common days
            ('0001-01-01', date(1, 1, 1)),
            ('1906-12-09', date(1906, 12, 9)),
            ('1970-01-01', date(1970, 1, 1)),
            ('2021-08-30', date(2021, 8, 30)),
            ('2999-12-31', date(2999, 12, 31)),
            # Months with 31 days
            ('2020-01-31', date(2020, 1, 31)),
            ('2021-03-31', date(2021, 3, 31)),
            ('2022-07-31', date(2022, 7, 31)),
            # Leap years
            ('1996-02-29', date(1996, 2, 29)),
            ('2000-02-29', date(2000, 2, 29)),
            ('2020-02-29', date(2020, 2, 29)),
            ('2024-02-29', date(2024, 2, 29)),
            ('2400-02-29', date(2400, 2, 29)),
        ]
    )
    def test_valid_dates(input_string, expected_date):
        """ Test DateValidator with valid YYYY-MM-DD date strings. """
        validator = DateValidator()
        validated_date = validator.validate(input_string)
        assert type(validated_date) is date
        assert validated_date == expected_date

    @staticmethod
    @pytest.mark.parametrize(
        'input_string', [
            # Nonsense strings
            '', 'banana', 'aaaa-bb-cc', '-01-01', '-0001-01-01', '-001-01-01',
            # Invalid year/month/day components
            '0000-00-00', '0000-01-01', '2020-00-01', '2020-01-00', '2020-13-01', '2020-01-32', '9999-99-99',
            # Invalid days per months
            '2020-02-30', '2020-04-31', '2020-11-31',
            # 29th February in non-leap years
            '2021-02-29', '1900-02-29', '2100-02-29',
        ]
    )
    def test_invalid_dates(input_string):
        """ Test DateValidator with invalid date strings. """
        validator = DateValidator()
        with pytest.raises(InvalidDateError) as exception_info:
            validator.validate(input_string)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_date',
            'date_format': 'YYYY-MM-DD',
        }
