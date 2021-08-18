# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import copy
import pytest

from wtfjson.helpers import Default, DefaultFactory, DefaultUnset, NoDefault, UnsetValue


class DefaultTest:
    """ Tests for the base Default class. """

    @staticmethod
    def test_default_none():
        """ Test Default object with None value. """
        default = Default(None)
        assert repr(default) == 'Default(None)'
        assert default.get_value() is None

    @staticmethod
    def test_default_integer():
        """ Test Default object with some integer value. """
        default = Default(42)
        assert repr(default) == 'Default(42)'
        assert default.get_value() == 42

    @staticmethod
    def test_default_list_deepcopied():
        """ Test Default object with a list, make sure that it is deepcopied. """
        default_list = []
        default = Default(default_list)
        assert repr(default) == 'Default([])'
        assert default.get_value() == []

        # Make sure list was copied by checking if the Default object value is modified when modifying the original list
        default_list.append(3)
        assert repr(default) == 'Default([])'
        assert default.get_value() == []


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
        value1 = default_factory.get_value()
        value2 = default_factory.get_value()
        assert value1 == [] and value2 == []
        assert value1 is not value2

    @staticmethod
    def test_default_factory_lambda():
        """ Test DefaultFactory with a lambda function. """
        # This lambda function will create a new list and return its object ID, which will be a different one each time.
        default_factory = DefaultFactory(lambda: id(list()))
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
        assert default_factory.get_value() == 1
        assert default_factory.get_value() == 2
        assert default_factory.get_value() == 3


class DefaultUnsetTest:
    """ Tests for the DefaultUnset class. """

    @staticmethod
    def test_default_unset():
        """ Test the DefaultUnset class. """
        default = DefaultUnset()
        assert repr(default) == 'DefaultUnset()'
        assert default.get_value() is UnsetValue


class NoDefaultTest:
    """ Tests for the NoDefault sentinel. """

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
        assert default1 is default2 is NoDefault

    @staticmethod
    def test_no_default_call():
        """ Test that calling NoDefault returns the sentinel itself. """
        assert NoDefault() is NoDefault
