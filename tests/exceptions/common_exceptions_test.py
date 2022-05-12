"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from validataclass.exceptions import ValidationError, InvalidTypeError


class ValidationErrorTest:
    """
    Tests for the ValidationError exception class.
    """

    @staticmethod
    @pytest.mark.parametrize(
        'code, kwargs, expected_repr', [
            (
                None,
                {},
                "ValidationError(code='unknown_error')"
            ),
            (
                'unit_test_error',
                {},
                "ValidationError(code='unit_test_error')"
            ),
            (
                None,
                {'reason': 'This is fine.'},
                "ValidationError(code='unknown_error', reason='This is fine.')"
            ),
            (
                'unit_test_error',
                {'reason': 'This is fine.', 'fruit': 'banana', 'number': 123},
                "ValidationError(code='unit_test_error', reason='This is fine.', fruit='banana', number=123)",
            ),
        ]
    )
    def test_validation_error_with_parameters(code, kwargs, expected_repr):
        """ Tests ValidationError with various parameters. """
        error = ValidationError(code=code, **kwargs)

        expected_code = code if code is not None else 'unknown_error'
        assert repr(error) == expected_repr
        assert str(error) == repr(error)
        assert error.to_dict() == {
            'code': expected_code,
            **kwargs,
        }

    @staticmethod
    @pytest.mark.parametrize(
        'code, kwargs, expected_repr', [
            (
                None,
                {},
                "UnitTestValidatonError(code='unit_test_error')"
            ),
            (
                None,
                {'reason': 'This is fine.'},
                "UnitTestValidatonError(code='unit_test_error', reason='This is fine.')"
            ),
            (
                'unit_test_error',
                {'reason': 'This is fine.', 'fruit': 'banana', 'number': 123},
                "UnitTestValidatonError(code='unit_test_error', reason='This is fine.', fruit='banana', number=123)",
            ),
        ]
    )
    def test_validation_error_subclass(code, kwargs, expected_repr):
        """ Tests subclassing ValidationError. """

        class UnitTestValidatonError(ValidationError):
            code = 'unit_test_error'

        error = UnitTestValidatonError(code=code, **kwargs)

        expected_code = code if code is not None else 'unit_test_error'
        assert repr(error) == expected_repr
        assert str(error) == repr(error)
        assert error.to_dict() == {
            'code': expected_code,
            **kwargs,
        }


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
