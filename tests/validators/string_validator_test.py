# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, StringTooShortError, StringTooLongError
from wtfjson.validators import StringValidator


class StringValidatorTest:
    @staticmethod
    def test_valid_string():
        validator = StringValidator()
        assert validator.validate('') == ''
        assert validator.validate('unit test banana') == 'unit test banana'

    @staticmethod
    def test_invalid_none():
        validator = StringValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        validator = StringValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    # Test length requirement checks: Only min_length specified

    @staticmethod
    @pytest.mark.parametrize('input_data', ['abc', 'banana', '1234567890abcdef'])
    def test_string_min_length_valid(input_data):
        validator = StringValidator(min_length=3)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'a', 'ab'])
    def test_string_min_length_too_short(input_data):
        validator = StringValidator(min_length=3)
        with pytest.raises(StringTooShortError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_short',
            'min_length': 3,
        }

    # Test length requirement checks: Only max_length specified

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'a', 'banana', '1234567890'])
    def test_string_max_length_valid(input_data):
        validator = StringValidator(max_length=10)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize('input_data', ['1234567890a', '1234567890abcdef'])
    def test_string_max_length_too_long(input_data):
        validator = StringValidator(max_length=10)
        with pytest.raises(StringTooLongError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_long',
            'max_length': 10,
        }

    # Test length requirement checks: Both min_length and max_length specified

    @staticmethod
    @pytest.mark.parametrize('input_data', ['abc', 'banana', '1234567890'])
    def test_string_min_max_length_valid(input_data):
        validator = StringValidator(min_length=3, max_length=10)
        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize('input_data', ['', 'a', 'ab'])
    def test_string_min_max_length_too_short(input_data):
        validator = StringValidator(min_length=3, max_length=10)
        with pytest.raises(StringTooShortError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_short',
            'min_length': 3,
            'max_length': 10,
        }

    @staticmethod
    @pytest.mark.parametrize('input_data', ['1234567890a', '1234567890abcdef'])
    def test_string_min_max_length_too_long(input_data):
        validator = StringValidator(min_length=3, max_length=10)
        with pytest.raises(StringTooLongError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'string_too_long',
            'min_length': 3,
            'max_length': 10,
        }
