# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError
from wtfjson.validators import BooleanValidator


class BooleanValidatorTest:
    @staticmethod
    def test_valid_bool():
        """ Test BooleanValidator with valid booleans. """
        validator = BooleanValidator()
        assert validator.validate(True) is True
        assert validator.validate(False) is False

    @staticmethod
    def test_invalid_none():
        """ Check that BooleanValidator raises exception for None as vvalue. """
        validator = BooleanValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', 'True', 1, 1.234, [True]])
    def test_invalid_wrong_type(input_data):
        """ Check that BooleanValidator raises exceptions for values that are not of type 'bool'. """
        validator = BooleanValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'bool',
        }

    # Tests for allow_strings=True option

    @staticmethod
    def test_allow_strings_valid():
        """ Test BooleanValidator with allow_strings=True option with valid strings. """
        validator = BooleanValidator(allow_strings=True)

        for input_str in ['True', 'true', 'TRUE']:
            assert validator.validate(input_str) is True
        for input_str in ['False', 'false', 'FALSE']:
            assert validator.validate(input_str) is False

    @staticmethod
    @pytest.mark.parametrize('input_data', ['banana', '', '0', '1', 'tru'])
    def test_allow_strings_invalid_strings(input_data):
        """ Test BooleanValidator with allow_strings=True option with invalid strings. """
        validator = BooleanValidator(allow_strings=True)
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'bool',
        }
