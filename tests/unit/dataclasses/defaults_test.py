"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from copy import copy
from typing import Any

import pytest

from validataclass.dataclasses import BaseDefault, Default, DefaultFactory, DefaultUnset, NoDefault
from validataclass.helpers import UnsetValue


# Create a non-abstract subclass of BaseDefault to test methods inherited from BaseDefault
class ExampleDefaultClass(BaseDefault[int]):
    def get_value(self) -> int:
        return 42

    def needs_factory(self) -> bool:
        return False


class BaseDefaultTest:
    """ Tests for the BaseDefault abstract base class. """

    @staticmethod
    def test_base_default_repr():
        assert repr(ExampleDefaultClass()) == 'ExampleDefaultClass'

    @staticmethod
    def test_base_default_equality():
        default1 = ExampleDefaultClass()
        default2 = ExampleDefaultClass()
        assert default1 == default1
        assert default1 != default2

    @staticmethod
    def test_base_default_hashable():
        default = ExampleDefaultClass()
        assert hash(default) == object.__hash__(default)


class DefaultTest:
    """ Tests for the Default class. """

    @staticmethod
    @pytest.mark.parametrize(
        'value, expected_repr',
        [
            (None, 'Default(None)'),
            (True, 'Default(True)'),
            (False, 'Default(False)'),
            (UnsetValue, 'Default(UnsetValue)'),
            (42, 'Default(42)'),
            (1.234, 'Default(1.234)'),
            ('banana', "Default('banana')"),
        ],
    )
    def test_default_immutable_values(value, expected_repr):
        """ Test Default object with different immutable values. """
        default = Default(value)

        # Check string representation and value
        assert repr(default) == expected_repr
        assert default.get_value() == value

        # Immutable values do not need a factory
        assert not default.needs_factory()

    @staticmethod
    def test_default_list_deepcopied():
        """ Test Default object with a list, make sure that it is deepcopied. """
        default_list: list[Any] = []
        default = Default(default_list)

        # Check string representation and value
        assert repr(default) == 'Default([])'
        assert default.get_value() == []
        assert default.needs_factory()

        # Make sure list was copied by checking if the Default object value is modified when modifying the original list
        default_list.append(3)
        assert repr(default) == 'Default([])'
        assert default.get_value() == []

        # Make sure list is copied every time the default value is used
        value1 = default.get_value()
        value2 = default.get_value()
        assert value1 is not value2

    @staticmethod
    def test_default_equality():
        """ Test equality and non-equality of Default objects. """
        assert Default(None) == Default(None)
        assert Default(UnsetValue) == Default(UnsetValue)
        assert Default(0) == Default(0)
        assert Default('') == Default('')
        assert Default([]) == Default([])

    @staticmethod
    @pytest.mark.parametrize(
        'first, second',
        [
            (Default(None), None),
            (Default(None), Default(0)),
            (Default(None), Default(UnsetValue)),
            (Default(0), 0),
            (Default(0), Default('')),
            (Default([]), Default([0])),
            (Default([]), Default({})),
        ],
    )
    def test_default_non_equality(first, second):
        """ Test non-equality between Default and other objects. """
        assert first != second
        assert second != first

    @staticmethod
    @pytest.mark.parametrize(
        'value',
        [
            None,
            0,
            42,
            'banana',
        ],
    )
    def test_default_hashable(value):
        """ Test hashability (__hash__) of Default objects. """
        assert hash(Default(value)) == hash(value)

    @staticmethod
    def test_default_not_callable():
        """ Test that default objects are not callable, except for the (deprecated) case of UnsetValue. """
        default = Default(None)
        with pytest.raises(TypeError, match="'Default' object is not callable"):
            default()


class DefaultFactoryTest:
    """ Tests for the DefaultFactory class. """

    @staticmethod
    def test_default_factory_repr():
        """ Test DefaultFactory __repr__ method. """
        assert repr(DefaultFactory(list)) == "DefaultFactory(<class 'list'>)"

    @staticmethod
    def test_default_factory_list():
        """ Test DefaultFactory with `list` as default generator. """
        default_factory: DefaultFactory[list[int]] = DefaultFactory(list)
        assert default_factory.needs_factory()

        # Generate values and test that they are not the same objects
        value1 = default_factory.get_value()
        value2 = default_factory.get_value()
        assert value1 == [] and value2 == []
        assert value1 is not value2

    @staticmethod
    def test_default_factory_lambda():
        """ Test DefaultFactory with a lambda function. """
        # This lambda function will create a new list and return its object ID, which will be a different one each time.
        default_factory = DefaultFactory(lambda: id(list()))
        assert default_factory.needs_factory()

        # Generate values and test that they are different from each other
        value1 = default_factory.get_value()
        value2 = default_factory.get_value()
        assert type(value1) is int and type(value2) is int
        assert value1 != value2

    @staticmethod
    def test_default_factory_counter_function():
        """ Test DefaultFactory with a counter function. """

        def counter():
            """
            Function that counts up every time it is called and saves the current number as an attribute of itself.
            """
            current = getattr(counter, 'current', 0) + 1
            setattr(counter, 'current', current)
            return current

        default_factory = DefaultFactory(counter)
        assert default_factory.needs_factory()

        # Generate values and check that they are counting upwards
        assert default_factory.get_value() == 1
        assert default_factory.get_value() == 2
        assert default_factory.get_value() == 3

    @staticmethod
    def test_default_factory_equality():
        """ Test equality and non-equality of DefaultFactory objects. """

        def example_fun():
            return 42

        assert DefaultFactory(list) == DefaultFactory(list)
        assert DefaultFactory(example_fun) == DefaultFactory(example_fun)

    @staticmethod
    @pytest.mark.parametrize(
        'first, second',
        [
            (DefaultFactory(list), list),
            (DefaultFactory(list), DefaultFactory(dict)),
            (DefaultFactory(lambda: 1), DefaultFactory(lambda: 2)),
            (DefaultFactory(lambda: 0), 0),
            (DefaultFactory(lambda: 0), Default(0)),
            (DefaultFactory(lambda: 0), DefaultUnset),
        ],
    )
    def test_default_factory_non_equality(first, second):
        """ Test non-equality between DefaultFactory and other objects. """
        assert first != second
        assert second != first

    @staticmethod
    def test_default_factory_hashable():
        """ Test hashability (__hash__) of DefaultFactory objects. """
        assert hash(DefaultFactory(list)) == hash(list)


class DefaultUnsetTest:
    """ Tests for the DefaultUnset object, formerly a subclass, now an alias for `Default(UnsetValue)`. """

    @staticmethod
    def test_default_unset():
        """ Test the DefaultUnset object. """
        assert isinstance(DefaultUnset, Default)
        assert repr(DefaultUnset) == 'Default(UnsetValue)'
        assert DefaultUnset.get_value() is UnsetValue
        assert not DefaultUnset.needs_factory()

    @staticmethod
    def test_default_unset_equality():
        """ Test equality of DefaultUnset with Default(UnsetValue). """
        assert DefaultUnset == Default(UnsetValue)
        assert Default(UnsetValue) == DefaultUnset

    @staticmethod
    @pytest.mark.parametrize(
        'other',
        [
            UnsetValue,
            None,
            Default(None),
            Default(0),
            DefaultFactory(lambda: None),
        ],
    )
    def test_default_unset_non_equality(other):
        """ Test non-equality between DefaultUnset and other objects. """
        assert DefaultUnset != other
        assert other != DefaultUnset

    @staticmethod
    def test_default_unset_call_is_deprecated():
        """ Test that calling DefaultUnset returns the object itself, but issues a deprecation warning. """
        with pytest.deprecated_call():
            assert DefaultUnset() is DefaultUnset


class NoDefaultTest:
    """ Tests for the NoDefault sentinel object. """

    @staticmethod
    def test_no_default():
        """ Test the NoDefault sentinel's behaviour as a Default object. """
        assert repr(NoDefault) == 'NoDefault'

        # get_value() must raise an exception
        with pytest.raises(ValueError, match=r'^No default value specified!$'):
            NoDefault.get_value()

        # needs_factory() must raise an exception
        with pytest.raises(NotImplementedError, match=r'^NoDefault can be used neither as a value nor as a factory\.$'):
            NoDefault.needs_factory()

    @staticmethod
    def test_no_default_is_unique():
        """ Test that NoDefault cannot be cloned. """
        default1 = NoDefault
        default2 = copy(NoDefault)
        assert default1 == default2
        assert default1 is default2 is NoDefault

    @staticmethod
    @pytest.mark.parametrize(
        'other',
        [
            None,
            Default(None),
            UnsetValue,
            DefaultUnset,
            DefaultFactory(lambda: None),
        ],
    )
    def test_no_default_non_equality(other):
        """ Test non-equality between NoDefault and other objects. """
        assert NoDefault != other
        assert other != NoDefault

    @staticmethod
    def test_no_default_hashable():
        """ Test that NoDefault is hashable (i.e. implements __hash__). """
        assert hash(NoDefault) == object.__hash__(NoDefault)

    @staticmethod
    def test_no_default_call_is_deprecated():
        """ Test that calling NoDefault returns the sentinel object itself, but issues a deprecation warning. """
        with pytest.deprecated_call():
            assert NoDefault() is NoDefault
