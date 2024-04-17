"""
validataclass
Copyright (c) 2024, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from validataclass.exceptions import ValidationError


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
