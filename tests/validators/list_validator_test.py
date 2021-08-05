# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
import pytest

from wtfjson.exceptions import RequiredValueError, InvalidTypeError, ListItemsValidationError
from wtfjson.validators import ListValidator, IntegerValidator, StringValidator, DecimalValidator


class ListValidatorTest:
    @staticmethod
    def test_valid_integer_list():
        validator = ListValidator(item_validator=IntegerValidator())
        assert validator.validate([123, 0, -42]) == [123, 0, -42]

    @staticmethod
    def test_valid_integer_list_empty():
        validator = ListValidator(item_validator=IntegerValidator())
        assert validator.validate([]) == []

    @staticmethod
    def test_valid_decimal_list():
        validator = ListValidator(item_validator=DecimalValidator())
        output_list = validator.validate(['3.1415', '-0.42', '0'])
        assert all(isinstance(item, Decimal) for item in output_list)
        assert output_list == [Decimal('3.1415'), Decimal('-0.42'), Decimal('0')]

    @staticmethod
    def test_valid_nested_list():
        input_list = [['3.1415', '42', '0'], ['-1.2', '2.4']]
        expected_list = [[Decimal('3.1415'), Decimal('42'), Decimal('0')], [Decimal('-1.2'), Decimal('2.4')]]

        validator = ListValidator(ListValidator(DecimalValidator()))
        output_list = validator.validate(input_list)

        for sublist in output_list:
            assert isinstance(sublist, list)
            assert all(isinstance(item, Decimal) for item in sublist)
        assert output_list == expected_list

    @staticmethod
    def test_invalid_none():
        validator = ListValidator(item_validator=IntegerValidator())
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_not_a_list():
        validator = ListValidator(item_validator=StringValidator())
        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate({'foo': 'bar'})
        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'list',
        }

    @staticmethod
    def test_invalid_decimal_list_items():
        validator = ListValidator(item_validator=DecimalValidator())
        with pytest.raises(ListItemsValidationError) as exception_info:
            # Indices 1 and 4 are valid; indices 0, 2, 3 raise errors
            validator.validate([12, '1.234', None, 'foobar', '42'])

        assert exception_info.value.to_dict() == {
            'code': 'list_item_errors',
            'item_errors': {
                0: {'code': 'invalid_type', 'expected_type': 'str'},
                2: {'code': 'required_value'},
                3: {'code': 'invalid_decimal'},
            }
        }

    # TODO: Nested list of dicts/dataclasses
