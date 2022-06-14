"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from decimal import Decimal

import pytest

from validataclass.dataclasses import validataclass, ValidataclassMixin, Default, DefaultUnset
from validataclass.helpers import OptionalUnset, UnsetValue
from validataclass.validators import DataclassValidator, DecimalValidator, IntegerValidator, StringValidator


@validataclass
class UnitTestDataclass(ValidataclassMixin):
    foo: int = IntegerValidator()  # required field
    bar: str = (StringValidator(), Default('bloop'))
    baz: OptionalUnset[Decimal] = (DecimalValidator(), DefaultUnset)


class ValidataclassMixinTest:
    """ Tests for the ValidataclassMixin class. """

    # Tests for to_dict() method

    @staticmethod
    def test_validataclass_to_dict():
        """ Tests the to_dict() method of the ValidataclassMixin class using the regular constructor. """
        obj = UnitTestDataclass(foo=42, bar='meep', baz=Decimal('-1.23'))
        assert obj.to_dict() == {
            'foo': 42,
            'bar': 'meep',
            'baz': Decimal('-1.23'),
        }

    @staticmethod
    def test_validataclass_to_dict_validated():
        """ Tests the to_dict() method of the ValidataclassMixin class using a DataclassValidator. """
        validator = DataclassValidator(UnitTestDataclass)
        obj: UnitTestDataclass = validator.validate({'foo': 42, 'bar': 'meep', 'baz': '-1.23'})
        assert obj.to_dict() == {
            'foo': 42,
            'bar': 'meep',
            'baz': Decimal('-1.23'),
        }

    @staticmethod
    def test_validataclass_to_dict_validated_with_defaults():
        """ Tests the to_dict() method of the ValidataclassMixin class using a DataclassValidator, with default values. """
        validator = DataclassValidator(UnitTestDataclass)
        obj: UnitTestDataclass = validator.validate({'foo': 42})
        assert obj.to_dict() == {
            'foo': 42,
            'bar': 'bloop',
        }

    @staticmethod
    def test_validataclass_to_dict_validated_keep_unset_values():
        """ Tests the to_dict() method of the ValidataclassMixin class with the parameter keep_unset_value=True. """
        validator = DataclassValidator(UnitTestDataclass)
        obj: UnitTestDataclass = validator.validate({'foo': 42})
        obj_as_dict = obj.to_dict(keep_unset_values=True)
        assert obj_as_dict == {
            'foo': 42,
            'bar': 'bloop',
            'baz': UnsetValue,
        }
        assert obj_as_dict['baz'] is UnsetValue

    # Tests for create_with_defaults() class method

    @staticmethod
    def test_create_with_defaults():
        """ Tests the create_with_defaults() class method, only with required fields. """
        with pytest.deprecated_call():
            obj = UnitTestDataclass.create_with_defaults(foo=42)

        assert isinstance(obj, UnitTestDataclass)
        assert obj.to_dict() == {
            'foo': 42,
            'bar': 'bloop',
        }
        assert obj.to_dict(keep_unset_values=True) == {
            'foo': 42,
            'bar': 'bloop',
            'baz': UnsetValue,
        }

    @staticmethod
    def test_create_with_defaults_overwrite_defaults():
        """ Tests the create_with_defaults() class method with explicitly set optional fields. """
        with pytest.deprecated_call():
            obj = UnitTestDataclass.create_with_defaults(foo=42, bar='meep', baz=Decimal('-1.23'))

        assert isinstance(obj, UnitTestDataclass)
        assert obj.to_dict() == {
            'foo': 42,
            'bar': 'meep',
            'baz': Decimal('-1.23'),
        }

    @staticmethod
    def test_create_with_defaults_invalid_required_fields():
        """ Tests the create_with_defaults() class method missing required fields. """
        # The exact exception message changed between Python versions 3.9 and 3.10
        with pytest.raises(TypeError, match="required keyword-only argument: 'foo'"):
            with pytest.deprecated_call():
                UnitTestDataclass.create_with_defaults()
