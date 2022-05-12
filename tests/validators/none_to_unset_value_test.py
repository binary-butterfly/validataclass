"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from decimal import Decimal

import pytest

from validataclass.exceptions import ValidationError
from validataclass.helpers import UnsetValue
from validataclass.validators import NoneToUnsetValue, DecimalValidator


class NoneToUnsetValueTest:
    """
    Unit tests for the NoneToUnsetValue wrapper.
    """

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_result',
        [
            (None, UnsetValue),
            ('12.34', Decimal('12.34')),
        ]
    )
    def test_valid(input_data, expected_result):
        """ Test NoneToUnsetValue with different valid input (None and non-None). """
        validator = NoneToUnsetValue(DecimalValidator())
        result = validator.validate(input_data)

        assert type(result) == type(expected_result)
        assert result == expected_result

    @staticmethod
    def test_invalid_type():
        """ Test that NoneToUnsetValue correctly re-raises or ignores validation errors from the wrapped validator. """
        validator = NoneToUnsetValue(DecimalValidator())

        with pytest.raises(ValidationError) as exception_info:
            validator.validate(123)

        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['none', 'str'],
        }
