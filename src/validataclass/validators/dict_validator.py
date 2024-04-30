"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Dict, List, Optional, Set

from validataclass.exceptions import (
    DictFieldsValidationError,
    DictInvalidKeyTypeError,
    DictRequiredFieldError,
    InvalidValidatorOptionException,
    ValidationError,
)
from .validator import Validator

__all__ = [
    'DictValidator',
]


class DictValidator(Validator):
    """
    Validator for dictionaries with all kinds of data.

    There are two ways to specify which validators to use to validate the dictionary's fields:
    - `field_validators` is a dictionary that maps field names to specific validators.
    - `default_validator` specifies a validator that is used for all fields *not* specified in `field_validators`.

    If no `default_validator` is defined, fields that are not specified in `field_validators` will be discarded.

    By default, all fields specified in `field_validators` are required fields, meaning the fields need to exist in a
    given input dictionary. You can override this by setting `required_fields` to a list of field names that should be
    required. Alternatively you can set `optional_fields` to only specify the fields that are NOT required.
    (Setting both `required_fields` and `optional_fields` will result in an error.)

    Examples:

    ```
    # Validator for a dict with three fields: "id" (integer), "name" (string), "price" (non-negative Decimal)
    # All three fields are required; fields with keys other than "id", "name" and "price" will be discarded.
    DictValidator(field_validators={
        'id': IntegerValidator(),
        'name': StringValidator(),
        'price': DecimalValidator(min_value='0'),
    })

    # Same as above, but this time only "id" and "name" are required, "price" is an optional field.
    # The output dict will only have the optional "price" field, if the input dict has it too.
    DictValidator(field_validators={
        'id': IntegerValidator(),
        'name': StringValidator(),
        'price': DecimalValidator(min_value='0'),
    }, required_fields=['id', 'name'])

    # Note: In the validator above, you could also specify optional_fields=['price'] instead of required_fields.

    # Validator for a dict with arbitrary keys (as long as they are strings), all values are validated as integers
    # No fields are required; output dict will have the same keys as the input dict with validated integers
    DictValidator(default_validator=IntegerValidator())
    ```

    Valid input: `{"field1": field1_value, "field2": field2_value, ...}`
    Output: `{"field1": validated_field1_value, "field2": validated_field2_value, ...}`
    """

    # Dictionary to specify which validators are applied to which fields of the input dictionary
    field_validators: Dict[str, Validator]

    # Validator that is applied to all fields not specified in field_validators
    default_validator: Optional[Validator]

    # Set of required fields
    required_fields: Set[str]

    def __init__(
        self,
        *,
        field_validators: Optional[Dict[str, Validator]] = None,
        default_validator: Optional[Validator] = None,
        required_fields: Optional[List[str]] = None,
        optional_fields: Optional[List[str]] = None
    ):
        """
        Creates a `DictValidator`.

        At least one of the parameters `field_validators` and `default_validator` is required (both can be combined).
        The parameters `required_fields` and `optional_fields` are mutually exclusive (cannot be combined).
        See class documentation (above) for more information.

        Parameters:
             `field_validators`: Dictionary, maps field names to validators
             `default_validator`: Validator for all fields not specified in `field_validators`
             `required_fields`: List of field names that must exist in a dict (default: all fields are required)
             `optional_fields`: List of field names that are not required (mutually exclusive with `required_fields`)
        """
        # For easier subclassing: If 'field_validators' etc. are already set (e.g. as class members in a subclass), use
        # those values as default for the constructor parameters. That way subclasses can simply define fields at class
        # scope without needing to define a custom __init__() method. Specifying the parameters explicitly in the
        # constructor still takes precedence over the defaults.
        if field_validators is None:
            field_validators = getattr(self, 'field_validators', None)
        if default_validator is None:
            default_validator = getattr(self, 'default_validator', None)
        if required_fields is None and optional_fields is None:
            required_fields = getattr(self, 'required_fields', None)

        # Check parameter validity
        if field_validators is None and default_validator is None:
            raise InvalidValidatorOptionException(
                'At least one of the parameters "field_validators" and "default_validator" needs to be specified.'
            )

        if required_fields is not None and optional_fields is not None:
            raise InvalidValidatorOptionException(
                'Parameters "required_fields" and "optional_fields" cannot be combined.'
            )

        # Set field and default validators
        self.field_validators = field_validators if field_validators is not None else {}
        self.default_validator = default_validator  # Can be None

        # Set required fields
        if required_fields is None:
            # Default to all fields specified in field_validators
            self.required_fields = set(field_validators.keys()) if field_validators is not None else set()
        else:
            self.required_fields = set(required_fields)

        # Remove optional fields from required fields
        if optional_fields is not None:
            self.required_fields = self.required_fields - set(optional_fields)

    def validate(self, input_data: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Validates input data. Returns a validated dict.
        """
        self._ensure_type(input_data, dict)

        # Check dictionary keys (must be strings)
        for key in input_data.keys():
            if type(key) is not str:
                raise DictInvalidKeyTypeError()

        field_errors: Dict[str, ValidationError] = {}
        validated_dict: Dict[str, Any] = {}

        # Check that required fields exist in input data
        for field_name in self.required_fields:
            if field_name not in input_data:
                field_errors[field_name] = DictRequiredFieldError()

        # Validate fields in input data
        for key, value in input_data.items():
            if key in self.field_validators:
                field_validator = self.field_validators.get(key)
            else:
                field_validator = self.default_validator

            # Silently ignore unknown fields (those not defined in field_validators) if no default validator is defined
            if field_validator is None:
                continue

            # Run field validator and catch validation errors
            try:
                validated_dict[key] = field_validator.validate_with_context(value, **kwargs)
            except ValidationError as error:
                field_errors[key] = error

        # If any field had a validation error, the dict validation fails
        if field_errors:
            raise DictFieldsValidationError(field_errors=field_errors)

        # No validation errors. Return validated dict. :)
        return validated_dict
