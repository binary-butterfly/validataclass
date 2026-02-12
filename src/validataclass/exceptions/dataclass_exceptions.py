"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

from typing_extensions import override

from .base_exceptions import ValidationError

__all__ = [
    'AdditionalPropertiesError',
    'DataclassPostValidationError',
]


class AdditionalPropertiesError(ValidationError):
    """
    Validation error raised by `DataclassValidator` when the input dictionary contains keys that do not correspond to
    any field in the dataclass, and `prevent_additional_properties` is set to `True`.

    The `additional_properties` attribute contains a sorted list of the extra field names.

    Example as dictionary:

    ```
    {
        'code': 'additional_properties',
        'additional_properties': ['unknown1', 'unknown2'],
    }
    ```
    """
    code = 'additional_properties'

    def __init__(self, *, additional_properties: list[str], **kwargs: Any):
        super().__init__(additional_properties=sorted(additional_properties), **kwargs)


class DataclassPostValidationError(ValidationError):
    """
    Validation error raised by `DataclassValidator` (or by a dataclass itself) when a user-defined post-validation
    condition fails.

    This is an "error container" similar to `DictFieldsValidationError`, i.e. it does not represent a specific error in
    itself, but *contains* one or multiple specific errors that happened at post-validation.

    This exception may contain a single field-independent validation error in the `error` attribute (for example, an
    arbitrary `ValidationError` raised by a `__post_validate__()` or `__post_init__()` method in a dataclass will be
    wrapped that way by the `DataclassValidator`), or may contain multiple field validation errors in the `field_errors`
    attribute (similar to `DictFieldsValidationError`), or both.

    The implementation of `to_dict()` recursively converts the field validation errors to dictionaries.

    Examples could look like this (as dictionaries):

    ```
    # Field-independent error:
    {
        'code': 'post_validation_errors',
        'error': {
            'code': 'some_validation_error',
        }
    }

    # Field errors:
    {
        'code': 'post_validation_errors',
        'field_errors': {
            'foo': {
                'code': 'field_required',
                'reason': 'The foo field is required when the bar field is defined.',
            }
        }
    }
    ```
    """
    code = 'post_validation_errors'
    wrapped_error: ValidationError | None = None
    field_errors: dict[str, ValidationError] | None = None

    def __init__(
        self,
        *,
        error: ValidationError | None = None,
        field_errors: dict[str, ValidationError] | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        # Wrap single validation error
        if error is not None:
            assert isinstance(error, ValidationError)
            self.wrapped_error = error

        # Wrap multiple errors associated with fields
        if field_errors is not None:
            assert all(isinstance(error, ValidationError) for error in field_errors.values())
            self.field_errors = field_errors

    @override
    def _get_repr_dict(self) -> dict[str, str]:
        base_dict = super()._get_repr_dict()

        if self.wrapped_error is not None:
            base_dict['error'] = repr(self.wrapped_error)
        if self.field_errors is not None and len(self.field_errors) > 0:
            base_dict['field_errors'] = repr(self.field_errors)

        return base_dict

    @override
    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()

        # Convert inner errors to dicts recursively
        if self.wrapped_error is not None:
            base_dict['error'] = self.wrapped_error.to_dict()
        if self.field_errors is not None and len(self.field_errors) > 0:
            base_dict['field_errors'] = {
                field_name: error.to_dict() for field_name, error in self.field_errors.items()
            }

        return base_dict
