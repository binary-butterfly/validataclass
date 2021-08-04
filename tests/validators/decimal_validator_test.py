# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
import pytest

from wtfjson.exceptions import ValidationError, RequiredValueError, InvalidTypeError
from wtfjson.validators import DecimalValidator


class DecimalValidatorTest:
    # TODO: parametrize, more tests
    @staticmethod
    def test_valid_decimal():
        validator = DecimalValidator()
        decimal = validator.validate('1.234')
        assert type(decimal) is Decimal
        assert decimal == Decimal('1.234')

    @staticmethod
    def test_invalid_none():
        validator = DecimalValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        validator = DecimalValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    # TODO: parametrize, more tests
    @staticmethod
    def test_invalid_malformed_string():
        validator = DecimalValidator()
        with pytest.raises(ValidationError) as exception_info:
            validator.validate('bananana')
        assert exception_info.value.to_dict() == {'code': 'invalid_decimal'}
