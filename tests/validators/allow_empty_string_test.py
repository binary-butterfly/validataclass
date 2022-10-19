"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from decimal import Decimal

import pytest
from validataclass.exceptions import ValidationError
from validataclass.validators import AllowEmptyString, DecimalValidator, IntegerValidator
from tests.test_utils import UnitTestContextValidator


class AllowEmptyStringTest:
    """
    Unit tests for the AllowEmptyString wrapper validator.
    """

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_result',
        [
            ('', ''),
            ('12.34', Decimal('12.34')),
        ]
    )
    def test_allow_empty_string_valid(input_data, expected_result):
        """ Test AllowEmptyString with different valid input (empty string ('') and not empty string). """
        validator = AllowEmptyString(DecimalValidator())
        result = validator.validate(input_data)

        assert type(result) == type(expected_result)
        assert result == expected_result

    @staticmethod
    @pytest.mark.parametrize(
        'input_data, expected_result',
        [
            ('', Decimal('3.1415')),
            ('12.34', Decimal('12.34')),
        ]
    )
    def test_allow_empty_string_with_default_valid(input_data, expected_result):
        """ Test AllowEmptyString with a custom default value with different valid input (empty string ('') and not empty string). """
        validator = AllowEmptyString(DecimalValidator(), default=Decimal('3.1415'))
        result = validator.validate(input_data)

        assert type(result) == type(expected_result)
        assert result == expected_result

    @staticmethod
    def test_allow_empty_string_with_context_arguments():
        """ Test that AllowEmptyString passes context arguments down to the wrapped validator. """
        validator = AllowEmptyString(UnitTestContextValidator())
        assert validator.validate('') == ''
        assert validator.validate('unittest') == "unittest / {}"
        assert validator.validate('unittest', foo=42) == "unittest / {'foo': 42}"

    @staticmethod
    def test_invalid_not_empty_string_value():
        """ Test that AllowEmptyString correctly wraps a specified validator and leaves (most) exceptions unmodified. """
        validator = AllowEmptyString(DecimalValidator())
        with pytest.raises(ValidationError) as exception_info:
            validator.validate('foobar')
        assert exception_info.value.to_dict() == {'code': 'invalid_decimal'}

    @staticmethod
    def test_invalid_type_contains_empty_string():
        """ Test that AllowEmptyString adds str to the expected_types parameter if the wrapped validator raises an InvalidTypeError. """
        validator = AllowEmptyString(IntegerValidator())
        with pytest.raises(ValidationError) as exception_info:
            validator.validate('unittest')
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types': ['int', 'str'],
        }

    @staticmethod
    def test_default_value_is_deepcopied():
        """
        Test that given default values are deepcopied. Otherwise using for example `default=[]` would always return a
        reference to the *same* list, and modifying this list would result in unexpected behaviour.
        """
        # Note: An empty list as default value for an IntegerValidator doesn't make a lot of sense, but simplifies the test.
        validator = AllowEmptyString(IntegerValidator(), default=[])
        first_list = validator.validate('')
        second_list = validator.validate('')
        assert first_list == []
        assert second_list == []

        # The lists are equal (both are empty lists), but they must not be the *same* object, otherwise bad stuff will happen.
        assert first_list is not second_list

    @staticmethod
    @pytest.mark.parametrize(
        'validator',
        [
            # Non-sense types
            '',
            'banana',

            # Validator class instead of instance (common mistake)
            IntegerValidator,
        ]
    )
    def test_invalid_validator_type(validator):
        """ Test that AllowEmptyString raises an exception on construction if the wrapped validator has the wrong type. """
        with pytest.raises(TypeError, match='AllowEmptyString requires a Validator instance'):
            AllowEmptyString(validator)  # noqa
