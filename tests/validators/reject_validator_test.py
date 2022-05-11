"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from tests.test_utils import UNSET_PARAMETER
from validataclass.exceptions import ValidationError, FieldNotAllowedError
from validataclass.validators import RejectValidator


class UnitTestValidationError(ValidationError):
    """
    Example exception to use as a custom error class in RejectValidator tests.
    """
    code = 'unit_test_error'


class RejectValidatorTest:
    """
    Unit tests for the RejectValidator.
    """

    # Tests with any non-None value

    @staticmethod
    @pytest.mark.parametrize('allow_none', [UNSET_PARAMETER, False, True])
    @pytest.mark.parametrize('input_data', [False, True, '', 'banana', 0, 123, []])
    def test_reject_anything_except_none(allow_none, input_data):
        """ Test that RejectValidator rejects anything (except None) with a FieldNotAllowedError. """
        validator = RejectValidator() if allow_none is UNSET_PARAMETER \
            else RejectValidator(allow_none=allow_none)

        with pytest.raises(FieldNotAllowedError) as exc_info:
            validator.validate(input_data)
        assert exc_info.value.to_dict() == {'code': 'field_not_allowed'}

    # Tests with None as input

    @staticmethod
    @pytest.mark.parametrize('allow_none', [UNSET_PARAMETER, False])
    def test_reject_none(allow_none):
        """ Test that RejectValidator rejects None if allow_none is not True. """
        validator = RejectValidator() if allow_none is UNSET_PARAMETER \
            else RejectValidator(allow_none=allow_none)

        with pytest.raises(FieldNotAllowedError) as exc_info:
            validator.validate(None)
        assert exc_info.value.to_dict() == {'code': 'field_not_allowed'}

    @staticmethod
    def test_allow_none():
        """ Test that RejectValidator allows None if allow_none is True. """
        validator = RejectValidator(allow_none=True)
        assert validator.validate(None) is None

    # Tests with custom errors

    @staticmethod
    @pytest.mark.parametrize(
        'error_class, error_code, error_reason, expected_error_code',
        [
            # Defaults
            (UNSET_PARAMETER, None, None, 'field_not_allowed'),

            # Default error class with custom error code and/or reason
            (UNSET_PARAMETER, None, 'This is a unit test.', 'field_not_allowed'),
            (UNSET_PARAMETER, 'custom_error_code', None, 'custom_error_code'),
            (UNSET_PARAMETER, 'custom_error_code', 'This is a unit test.', 'custom_error_code'),

            # Custom error class with default code and no reason
            (UnitTestValidationError, None, None, 'unit_test_error'),

            # Custom error class with custom error code and/or reason
            (UnitTestValidationError, None, 'This is a unit test.', 'unit_test_error'),
            (UnitTestValidationError, 'custom_error_code', None, 'custom_error_code'),
            (UnitTestValidationError, 'custom_error_code', 'This is a unit test.', 'custom_error_code'),
        ]
    )
    @pytest.mark.parametrize('input_data', [None, 0, 'banana'])
    def test_custom_errors(error_class, error_code, error_reason, expected_error_code, input_data):
        """ Test RejectValidator with various custom error settings. """
        # Build expectations
        expected_error_class = error_class if error_class is not UNSET_PARAMETER else FieldNotAllowedError
        expected_error_dict = {'code': expected_error_code}
        if error_reason is not None:
            expected_error_dict['reason'] = error_reason

        # Create validator
        validator = RejectValidator(error_code=error_code, error_reason=error_reason) if error_class is UNSET_PARAMETER \
            else RejectValidator(error_class=error_class, error_code=error_code, error_reason=error_reason)

        # Test validator
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(input_data)

        assert type(exc_info.value) is expected_error_class
        assert exc_info.value.to_dict() == expected_error_dict

    @staticmethod
    def test_custom_error_class_invalid_type():
        """ Test that RejectValidator raises an error on construction if the error class is not a ValidatonError subclass. """
        with pytest.raises(TypeError, match='Error class must be a subclass of ValidationError'):
            RejectValidator(error_class=Exception)  # noqa
