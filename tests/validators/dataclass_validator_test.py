# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional
import pytest

from wtfjson.exceptions import DictFieldsValidationError, RequiredValueError, InvalidValidatorOptionException, \
    DataclassInvalidFieldValidatorException

from wtfjson.validators import DataclassValidator, DecimalValidator, IntegerValidator, StringValidator
from wtfjson.helpers.dataclasses import validator_dataclass, validator_field


# Simple example dataclass

@validator_dataclass
class UnitTestDataclass:
    """
    Simple dataclass for testing DataclassValidator.
    """
    name: str = StringValidator()
    amount: int = IntegerValidator()
    weight: Decimal = DecimalValidator()
    # Currently, all fields with default values have to be defined at the end of a dataclass
    color: str = validator_field(StringValidator(), default='unknown color')


# More complex / nested dataclass

@validator_dataclass
class UnitTestNestedDataclass:
    """
    Complex dataclass that contains other dataclasses, used for testing nested DataclassValidators.
    """
    name: str = StringValidator()
    test_fruit: UnitTestDataclass = DataclassValidator(UnitTestDataclass)
    test_vegetable: Optional[UnitTestDataclass] = validator_field(DataclassValidator(UnitTestDataclass), default=None)


class DataclassValidatorTest:
    # Tests for DataclassValidator with a simple dataclass

    @staticmethod
    def test_dataclass_valid():
        """ Validate a dictionary as a dataclass, using valid data. """
        validator: DataclassValidator[UnitTestDataclass] = DataclassValidator(UnitTestDataclass)
        validated_data = validator.validate({
            'name': 'banana',
            'color': 'yellow',
            'amount': 10,
            'weight': '1.234',
            # Unknown fields will be ignored
            'unknown_field': 'unknown_value',
        })

        assert type(validated_data) is UnitTestDataclass
        assert validated_data.name == 'banana'
        assert validated_data.color == 'yellow'
        assert validated_data.amount == 10
        assert validated_data.weight == Decimal('1.234')

    @staticmethod
    def test_dataclass_invalid_none():
        """ Test a DataclassValidator with 'None' as input. """
        validator: DataclassValidator[UnitTestDataclass] = DataclassValidator(UnitTestDataclass)
        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)
        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_dataclass_invalid():
        """ Test a DataclassValidator with invalid and missing data. """
        validator: DataclassValidator[UnitTestDataclass] = DataclassValidator(UnitTestDataclass)

        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({
                'name': None,
                'color': 5,
                'amount': 'drei',
            })

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'name': {'code': 'required_value'},
                'color': {'code': 'invalid_type', 'expected_type': 'str'},
                'amount': {'code': 'invalid_type', 'expected_type': 'int'},
                'weight': {'code': 'required_field'},
            },
        }

    @staticmethod
    def test_dataclass_optional_field():
        """ Test optional fields in dataclasses. """
        validator: DataclassValidator[UnitTestDataclass] = DataclassValidator(UnitTestDataclass)
        validated_data = validator.validate({
            'name': 'apple',
            'amount': 3,
            'weight': '0.5',
            # Leaving out optional field 'color'
        })

        assert type(validated_data) is UnitTestDataclass
        assert validated_data.name == 'apple'
        # Check the default value
        assert validated_data.color == 'unknown color'
        assert validated_data.amount == 3
        assert validated_data.weight == Decimal('0.5')

    # Tests for subclassed DataclassValidators

    @staticmethod
    def test_subclassed_dataclass_validator():
        """ Test subclassing of DataclassValidator. """

        class UnitTestDataclassValidator(DataclassValidator[UnitTestDataclass]):
            dataclass_cls = UnitTestDataclass

        validator = UnitTestDataclassValidator()
        validated_data = validator.validate({
            'name': 'banana',
            'color': 'yellow',
            'amount': 10,
            'weight': '1.234',
        })

        assert type(validated_data) is UnitTestDataclass
        assert validated_data.name == 'banana'
        assert validated_data.color == 'yellow'
        assert validated_data.amount == 10
        assert validated_data.weight == Decimal('1.234')

    # Tests for more complex and nested validators using dataclasses

    @staticmethod
    def test_nested_dataclasses_valid():
        """ Validate nested dataclasses. """
        validator: DataclassValidator[UnitTestNestedDataclass] = DataclassValidator(UnitTestNestedDataclass)
        validated_data = validator.validate({
            'name': 'something with bananas',
            'test_fruit': {
                'name': 'banana',
                'amount': 3,
                'weight': '0.456',
                # Leaving out optional field 'color'
            },
            # Leaving out optional field 'test_vegetable'
        })

        # Check outer dataclass
        assert type(validated_data) is UnitTestNestedDataclass
        assert validated_data.name == 'something with bananas'

        # Check inner dataclass
        assert type(validated_data.test_fruit) is UnitTestDataclass
        assert validated_data.test_fruit.name == 'banana'
        assert validated_data.test_fruit.amount == 3
        assert validated_data.test_fruit.weight == Decimal('0.456')
        assert validated_data.test_fruit.color == 'unknown color'

        # Check default value
        assert validated_data.test_vegetable is None

    @staticmethod
    def test_nested_dataclasses_invalid():
        """ Validate nested dataclasses with invalid data. """
        validator: DataclassValidator[UnitTestNestedDataclass] = DataclassValidator(UnitTestNestedDataclass)

        with pytest.raises(DictFieldsValidationError) as exception_info:
            validator.validate({
                'name': 123,
                # Leaving out *required* field 'test_fruit'
                'test_vegetable': {
                    'name': 'banana',
                    'amount': 'banananana',
                },
            })

        assert exception_info.value.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'name': {'code': 'invalid_type', 'expected_type': 'str'},
                'test_fruit': {'code': 'required_field'},
                'test_vegetable': {
                    'code': 'field_errors',
                    'field_errors': {
                        'amount': {'code': 'invalid_type', 'expected_type': 'int'},
                        'weight': {'code': 'required_field'},
                    },
                },
            },
        }

    # Test invalid validator options

    @staticmethod
    def test_invalid_dataclass_validator_without_dataclass():
        """ Test that a DataclassValidator cannot be created without a dataclass. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DataclassValidator()

        assert str(exception_info.value) == "Parameter 'dataclass_cls' must be specified (or set as class member in a subclass)."

    @staticmethod
    def test_invalid_dataclass_validator_with_invalid_dataclass():
        """ Test that a DataclassValidator cannot be created with a class that is not a dataclass. """

        class Foo:
            bar: int = IntegerValidator()

        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            DataclassValidator(Foo)

        assert str(exception_info.value) == "Parameter 'dataclass_cls' must be a dataclass type."

    @staticmethod
    def test_invalid_dataclass_validator_with_dataclass_instance():
        """ Test that a DataclassValidator cannot be created with an *instance* of a dataclass. """
        with pytest.raises(InvalidValidatorOptionException) as exception_info:
            dataclass_instance = UnitTestDataclass(name='test', amount=3, weight=Decimal('1.234'))
            # Note: Type checkers will obviously complain about this line, the 'noqa' silences this warning.
            DataclassValidator(dataclass_instance)  # noqa

        assert str(exception_info.value) == "Parameter 'dataclass_cls' is a dataclass instance, but must be a dataclass type."

    # Test DataclassValidator with incompatible dataclasses

    @staticmethod
    def test_dataclass_field_without_validator():
        """ Test that DataclassValidator only allows dataclasses where every field has a defined Validator. """

        @dataclass
        class IncompatibleDataclass:
            # No validator specified
            foo: str = 'unknown'

        with pytest.raises(DataclassInvalidFieldValidatorException) as exception_info:
            DataclassValidator(IncompatibleDataclass)

        assert str(exception_info.value) == "Dataclass field 'foo' has no defined Validator."

    @staticmethod
    def test_dataclass_field_with_invalid_validator():
        """ Test that DataclassValidator only allows dataclasses where every field has a valid Validator. """

        @dataclass
        class IncompatibleDataclass:
            # Metadata contains 'validator' but it is not of type Validator
            foo: str = field(default='unknown', metadata={'validator': 'foobar'})

        with pytest.raises(DataclassInvalidFieldValidatorException) as exception_info:
            DataclassValidator(IncompatibleDataclass)

        assert str(exception_info.value) == "Validator specified for dataclass field 'foo' is not of type 'Validator')."
