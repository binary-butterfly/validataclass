# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError
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
