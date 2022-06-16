"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from copy import copy

import pytest

from validataclass.dataclasses import Default, DefaultFactory, DefaultUnset, NoDefault
from validataclass.helpers import UnsetValue


class DefaultTest:
    """ Tests for the base Default class. """

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
        ]
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
        default_list = []
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
        ]
    )
    def test_default_non_equality(first, second):
        """ Test non-equality between Default and other objects. """
        assert first != second
        assert second != first


class DefaultFactoryTest:
    """ Tests for the DefaultFactory class. """

    @staticmethod
    def test_default_factory_repr():
        """ Test DefaultFactory __repr__ method. """
        default_factory = DefaultFactory(list)
        assert repr(default_factory) == "DefaultFactory(<class 'list'>)"

    @staticmethod
    def test_default_factory_list():
        """ Test DefaultFactory with `list` as default generator. """
        default_factory = DefaultFactory(list)
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
            """ Function that counts up every time it is called and saves the current number as an attribute of itself. """
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
        ]
    )
    def test_default_factory_non_equality(first, second):
        """ Test non-equality between DefaultFactory and other objects. """
        assert first != second
        assert second != first


class DefaultUnsetTest:
    """ Tests for the DefaultUnset sentinel object. """

    @staticmethod
    def test_default_unset():
        """ Test the DefaultUnset sentinel object. """
        default = DefaultUnset
        assert repr(default) == 'DefaultUnset'
        assert default.get_value() is UnsetValue
        assert not default.needs_factory()

    @staticmethod
    def test_default_unset_is_unique():
        """ Test that DefaultUnset cannot be cloned. """
        default1 = DefaultUnset
        default2 = copy(DefaultUnset)
        assert default1 is default2 is DefaultUnset

    @staticmethod
    def test_default_unset_equality():
        """ Test equality between DefaultUnset and Default(UnsetValue) objects. """
        assert DefaultUnset == DefaultUnset
        assert DefaultUnset == Default(UnsetValue)
        assert Default(UnsetValue) == DefaultUnset

        assert DefaultUnset != Default(None)
        assert Default(None) != DefaultUnset

    @staticmethod
    @pytest.mark.parametrize('other', [UnsetValue, None, Default(None), Default(0), DefaultFactory(lambda: None)])
    def test_default_unset_non_equality(other):
        """ Test non-equality between DefaultUnset and other objects. """
        assert DefaultUnset != other
        assert other != DefaultUnset

    @staticmethod
    def test_default_unset_call():
        """ Test that calling DefaultUnset returns the sentinel object itself. """
        assert DefaultUnset() is DefaultUnset


class NoDefaultTest:
    """ Tests for the NoDefault sentinel object. """

    @staticmethod
    def test_no_default():
        """ Test the NoDefault sentinel's behaviour as a Default object. """
        default = NoDefault
        assert repr(default) == 'NoDefault'

        # get_value() must raise an exception
        with pytest.raises(ValueError) as exception_info:
            default.get_value()
        assert str(exception_info.value) == 'No default value specified!'

    @staticmethod
    def test_no_default_is_unique():
        """ Test that NoDefault cannot be cloned. """
        default1 = NoDefault
        default2 = copy(NoDefault)
        assert default1 == default2
        assert default1 is default2 is NoDefault

    @staticmethod
    @pytest.mark.parametrize('other', [None, Default(None), UnsetValue, DefaultUnset, DefaultFactory(lambda: None)])
    def test_no_default_non_equality(other):
        """ Test non-equality between NoDefault and other objects. """
        assert NoDefault != other
        assert other != NoDefault

    @staticmethod
    def test_no_default_call():
        """ Test that calling NoDefault returns the sentinel itself. """
        assert NoDefault() is NoDefault
