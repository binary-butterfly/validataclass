# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import copy
import pytest

from wtfjson.helpers import Default, NoDefault


class DefaultTest:
    # Tests for Default()

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


class NoDefaultTest:
    # Tests for the NoDefault sentinel

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
