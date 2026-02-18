"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from validataclass.exceptions import (
    UnknownFieldsError,
    DataclassPostValidationError,
    DictRequiredFieldError,
    InvalidTypeError,
    ValidationError,
)


class UnknownFieldsErrorTest:
    """
    Tests for the UnknownFieldsError exception class.
    """

    @staticmethod
    def test_unknown_fields_error_single_property():
        """ Tests UnknownFieldsError with a single additional property. """
        error = UnknownFieldsError(unknown_fields=['unknown_field'])

        assert error.to_dict() == {
            'code': 'unknown_fields',
            'unknown_fields': ['unknown_field'],
        }

    @staticmethod
    def test_unknown_fields_error_multiple_fields():
        """ Tests UnknownFieldsError with multiple additional fields (sorted). """
        error = UnknownFieldsError(unknown_fields=['watermelon', 'apple', 'mango'])

        assert error.to_dict() == {
            'code': 'unknown_fields',
            'unknown_fields': ['apple', 'mango', 'watermelon'],
        }

    @staticmethod
    def test_unknown_fields_error_repr():
        """ Tests repr of UnknownFieldsError. """
        error = UnknownFieldsError(unknown_fields=['unknown1', 'unknown2'])

        assert (
            repr(error)
            == "UnknownFieldsError(code='unknown_fields', "
               "unknown_fields=['unknown1', 'unknown2'])"
        )
        assert str(error) == repr(error)


class DataclassPostValidationErrorTest:
    """
    Tests for the DataclassPostValidationError exception class.
    """

    @staticmethod
    def test_dataclass_post_validation_error_with_global_error():
        """ Tests DataclassPostValidationError with a global wrapped error. """
        error = DataclassPostValidationError(
            error=ValidationError(code='example_error', reason='Something is wrong.'),
        )

        assert (
            repr(error)
            == "DataclassPostValidationError(code='post_validation_errors', "
               "error=ValidationError(code='example_error', reason='Something is wrong.'))"
        )

        assert str(error) == repr(error)
        assert error.to_dict() == {
            'code': 'post_validation_errors',
            'error': {
                'code': 'example_error',
                'reason': 'Something is wrong.',
            },
        }

    @staticmethod
    def test_dataclass_post_validation_error_with_field_errors():
        """ Tests DataclassPostValidationError with field errors. """
        error = DataclassPostValidationError(
            field_errors={
                'missing_field': DictRequiredFieldError(),
                'invalid_type_field': InvalidTypeError(expected_types=int),
            },
        )

        assert (
            repr(error)
            == "DataclassPostValidationError(code='post_validation_errors', field_errors={"
               "'missing_field': DictRequiredFieldError(code='required_field'), "
               "'invalid_type_field': InvalidTypeError(code='invalid_type', expected_type='int')})"
        )

        assert str(error) == repr(error)
        assert error.to_dict() == {
            'code': 'post_validation_errors',
            'field_errors': {
                'missing_field': {'code': 'required_field'},
                'invalid_type_field': {'code': 'invalid_type', 'expected_type': 'int'},
            },
        }

    @staticmethod
    def test_dataclass_post_validation_error_with_global_and_field_errors():
        """ Tests DataclassPostValidationError with both a global error and field errors. """
        error = DataclassPostValidationError(
            error=ValidationError(code='example_error', reason='Something is wrong.'),
            field_errors={
                'missing_field': DictRequiredFieldError(),
            }
        )

        assert (
            repr(error)
            == "DataclassPostValidationError(code='post_validation_errors', "
               "error=ValidationError(code='example_error', reason='Something is wrong.'), "
               "field_errors={'missing_field': DictRequiredFieldError(code='required_field')})"
        )

        assert str(error) == repr(error)
        assert error.to_dict() == {
            'code': 'post_validation_errors',
            'error': {
                'code': 'example_error',
                'reason': 'Something is wrong.',
            },
            'field_errors': {
                'missing_field': {'code': 'required_field'},
            },
        }
