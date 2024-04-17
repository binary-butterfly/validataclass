"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from validataclass.exceptions import InvalidTypeError


class InvalidTypeErrorTest:
    """
    Tests for the InvalidTypeError exception class.
    """

    @staticmethod
    @pytest.mark.parametrize(
        'types, expected_types_repr, expected_types_dict', [
            # Single expected type (as type or as string)
            (int, "expected_type='int'", {'expected_type': 'int'}),
            (type(None), "expected_type='none'", {'expected_type': 'none'}),
            ('banana', "expected_type='banana'", {'expected_type': 'banana'}),

            # List of expected types (as types or as strings; lists will be sorted alphabetically)
            ([int, float], "expected_types=['float', 'int']", {'expected_types': ['float', 'int']}),
            (['banana', type(None), int], "expected_types=['banana', 'int', 'none']", {'expected_types': ['banana', 'int', 'none']}),
        ]
    )
    def test_invalid_type_error(types, expected_types_repr, expected_types_dict):
        """ Tests InvalidTypeError with different expected_types parameters. """
        error = InvalidTypeError(expected_types=types)

        assert repr(error) == f"InvalidTypeError(code='invalid_type', {expected_types_repr})"
        assert str(error) == repr(error)
        assert error.to_dict() == {'code': 'invalid_type', **expected_types_dict}

    @staticmethod
    def test_add_expected_types():
        """ Tests adding types to a InvalidTypeError with `add_expected_types()`. """
        error = InvalidTypeError(expected_types=int)

        # Check error before adding types
        assert repr(error) == "InvalidTypeError(code='invalid_type', expected_type='int')"
        assert error.to_dict() == {'code': 'invalid_type', 'expected_type': 'int'}

        # Add additional types
        error.add_expected_type(float)
        error.add_expected_type('banana')

        # Check error after adding types
        assert repr(error) == "InvalidTypeError(code='invalid_type', expected_types=['banana', 'float', 'int'])"
        assert error.to_dict() == {'code': 'invalid_type', 'expected_types': ['banana', 'float', 'int']}

    @staticmethod
    def test_add_duplicate_to_expected_types():
        """ Tests adding duplicate to InvalidTypeError with `add_expected_types()` should not add new expected type. """
        error = InvalidTypeError(expected_types=[int, str])

        # Add duplicate additional types
        error.add_expected_type(int)

        # Check 'int' is not added to error
        assert repr(error) == "InvalidTypeError(code='invalid_type', expected_types=['int', 'str'])"
        assert error.to_dict() == {'code': 'invalid_type', 'expected_types': ['int', 'str']}
