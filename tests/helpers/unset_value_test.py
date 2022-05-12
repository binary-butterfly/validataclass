"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from copy import copy

import pytest

from validataclass.helpers import UnsetValue, UnsetValueType


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

    @staticmethod
    def test_unset_value_equal_to_itself():
        """ Test that UnsetValue is equal to itself. """
        assert UnsetValue == UnsetValue

    @staticmethod
    @pytest.mark.parametrize(
        'other_value', [None, False, True, object(), 0, '', 'UnsetValue', '<UnsetValue>', (UnsetValue,), [UnsetValue]]
    )
    def test_unset_value_not_equal(other_value):
        """ Test that nothing is equal to UnsetValue (except itself). """
        assert other_value != UnsetValue
        assert UnsetValue != other_value
