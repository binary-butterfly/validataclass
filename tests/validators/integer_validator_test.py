# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError
from wtfjson.validators import IntegerValidator


class IntegerValidatorTest:
    @staticmethod
    def test_valid_integer():
        validator = IntegerValidator()
        assert validator.validate(0) == 0
        assert validator.validate(123) == 123
        assert validator.validate(-456) == -456

    @staticmethod
    def test_invalid_none():
        validator = IntegerValidator()
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        validator = IntegerValidator()
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate('unit test banana')
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'int',
        }
