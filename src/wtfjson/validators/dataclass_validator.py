# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import dataclasses
from typing import Any, Optional, TypeVar, Generic

from . import Validator, DictValidator
from wtfjson.exceptions import InvalidValidatorOptionException, DataclassValidatorFieldException
from wtfjson.helpers import Default, NoDefault

# See also: `wtfjson.helpers.dataclasses`, which defines some helper functions to easily create DataclassValidator-friendly dataclasses.


# Type variable for type hints in DataclassValidator
T_Dataclass = TypeVar('T_Dataclass')


class DataclassValidator(DictValidator, Generic[T_Dataclass]):
    """
    Validator that converts dictionaries to instances of user-defined dataclasses with validated fields.

    The DataclassValidator is basically a specialized variant of the DictValidator that takes a dataclass with special metadata
    as parameter, which it uses to determine the dictionary fields, which validators to use for validating them, which fields are
    required or optional, and what default values to use for optional fields. Input data is first validated as a regular dictionary
    and then used to create an instance of the dataclass.

    In order to use a dataclass with this validator, each field of the dataclass needs to be defined with metadata that specifies a
    Validator (and optionally default values) for this field. This *can* be done manually using the regular Python dataclass
    function `dataclasses.field()` like this:

    ```
    @dataclass
    class ExampleDataclass:
        example_field: str = field(metadata={'validator': StringValidator()})
        optional_field: str = field(metadata={'validator': StringValidator(), 'default': Default('')})
    ```

    To simplify (and prettify) your dataclasses, there are also some helper functions in `wtfjson.helpers.dataclasses` that generate
    this metadata for you, e.g. the decorator `@validator_dataclass` and the function `validator_field()`. It is highly recommended
    to use these helpers instead of defining the metadata manually as it improves code readability.

    Equivalent example using the helper functions:

    ```
    @validator_dataclass
    class ExampleDataclass:
        example_field: str = StringValidator()
        optional_field: str = StringValidator(), Default('')

        # Also equivalent:
        # example_field: str = validator_field(StringValidator())
        # optional_field: str = validator_field(StringValidator(), default='')
    ```

    It is important to note that DataclassValidator implements its own mechanism for setting default values in optional fields instead
    of using the regular dataclass field defaults. This allows for more flexibility, for example you can define required and optional
    fields in any order, while in regular dataclasses all optional fields must be defined *after* the required fields. See the example
    above for how to specify default values.

    All fields that do not specify a default value (or explicitly use the special value `NoDefault`) are required.
    """

    # Dataclass type that the validated dictionary will be converted to
    dataclass_cls: type = None

    # Field default values
    field_defaults: dict[str, Default] = None

    def __init__(self, dataclass_cls: Optional[type] = None):
        # For easier subclassing: If 'self.dataclass_cls' is already set (e.g. as class member in a subclass), use this as the default.
        if dataclass_cls is None:
            dataclass_cls = getattr(self, 'dataclass_cls', None)

        # Check that dataclass_cls is actually a dataclass, and that it is the class itself and not an instance of it
        if dataclass_cls is None:
            raise InvalidValidatorOptionException('Parameter "dataclass_cls" must be specified (or set as class member in a subclass).')
        if not dataclasses.is_dataclass(dataclass_cls):
            raise InvalidValidatorOptionException('Parameter "dataclass_cls" must be a dataclass type.')
        if not isinstance(dataclass_cls, type):
            raise InvalidValidatorOptionException('Parameter "dataclass_cls" is a dataclass instance, but must be a dataclass type.')

        self.dataclass_cls = dataclass_cls
        self.field_defaults = {}

        # Collect field validators and required fields for the DictValidator by examining the dataclass fields
        field_validators = {}
        required_fields = []

        # Note: Pycharm falsely complains that we're calling dataclasses.fields() on something that is neither a dataclass instance nor
        # a type, even though we explicitly checked the type beforehand to ensure that it's really a dataclass type. Whatever, Pycharm...
        for field in dataclasses.fields(dataclass_cls):  # noqa
            field: dataclasses.Field  # (Type hint)

            # Skip fields with init=False, those are not validated
            if field.init is False:
                continue

            # Get validator for this field by parsing metadata, add to DictValidator fields
            field_validators[field.name] = self._get_field_validator(field)

            # Get default value for this field (if set), by parsing metadata
            field_default = self._get_field_default(field)
            if field_default is not NoDefault:
                self.field_defaults[field.name] = field_default

            # Make field optional if any kind of default value is set (including regular dataclass field defaults to keep compatibility)
            if field_default is NoDefault and field.default is dataclasses.MISSING and field.default_factory is dataclasses.MISSING:
                required_fields.append(field.name)

        # Initialize the underlying DictValidator
        super().__init__(field_validators=field_validators, required_fields=required_fields)

    @staticmethod
    def _get_field_validator(field: dataclasses.Field) -> Validator:
        # Parse field metadata to get Validator
        validator = field.metadata.get('validator')

        # Ensure that validator is defined and has a valid type
        if validator is None:
            raise DataclassValidatorFieldException(f'Dataclass field "{field.name}" has no defined Validator.')
        if not isinstance(validator, Validator):
            raise DataclassValidatorFieldException(f'Validator specified for dataclass field "{field.name}" is not of type "Validator".')
        return validator

    @staticmethod
    def _get_field_default(field: dataclasses.Field) -> Default:
        # Parse field metadata to get Default object
        default = field.metadata.get('validator_default', NoDefault)

        # Default is optional
        if default is NoDefault or default is None:
            return NoDefault

        # Ensure valid type
        if not isinstance(default, Default):
            raise DataclassValidatorFieldException(f'Default specified for dataclass field "{field.name}" is not of type "Default".')
        return default

    def validate(self, input_data: Any) -> T_Dataclass:
        """
        Validate an input dictionary according to the specified dataclass. Returns an instance of the dataclass.
        """
        # Validate raw dictionary using underlying DictValidator
        validated_dict = super().validate(input_data)

        # Fill optional fields with default values
        for field_name, field_default in self.field_defaults.items():
            if field_name not in validated_dict:
                validated_dict[field_name] = field_default.get_value()

        # Create dataclass object from validated dictionary
        return self.dataclass_cls(**validated_dict)
