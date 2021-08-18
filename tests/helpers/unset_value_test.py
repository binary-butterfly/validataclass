# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from copy import copy

from wtfjson.helpers import UnsetValue, UnsetValueType


class UnsetValueTest:
    """ Tests for the UnsetValue sentinel object and its type UnsetValueType. """

    @staticmethod
    def test_unset_value():
        """ Test UnsetValue and its magic methods. """
        assert type(UnsetValue) is UnsetValueType
        assert repr(UnsetValue) == 'UnsetValue'
        assert str(UnsetValue) == '<UnsetValue>'
        assert bool(UnsetValue) is False

    @staticmethod
    def test_unset_value_unique():
        """ Test that UnsetValue is a unique sentinel object, i.e. all UnsetValue values are the same. """
        unset_value1 = UnsetValue
        unset_value2 = copy(unset_value1)
        unset_value3 = UnsetValueType()
        assert unset_value1 is unset_value2 is unset_value3 is UnsetValue

        # Test that calling the UnsetValue returns the UnsetValue itself
        assert UnsetValue() is UnsetValue
