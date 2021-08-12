# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import dataclasses
from typing import Any, Optional, TypeVar, Generic

from . import Validator, DictValidator
from wtfjson.exceptions import InvalidValidatorOptionException, DataclassInvalidFieldValidatorException

# See also: `wtfjson.helpers.dataclasses`, which defines some helper functions to easily create DataclassValidator-friendly dataclasses.


# Type variable for type hints in DataclassValidator
T_Dataclass = TypeVar('T_Dataclass')


class DataclassValidator(DictValidator, Generic[T_Dataclass]):
    """
    Validator that converts dictionaries to instances of user-defined dataclasses with validated fields.

    The DataclassValidator is basically a specialized variant of the DictValidator that takes a dataclass with special metadata
    as parameter, which it uses to determine the dictionary fields, which validators to use for validating them, and which fields are
    required or optional. Input data is first validated as a regular dictionary and then used to create an instance of the dataclass.

    In order to use a dataclass with this validator, each field of the dataclass needs to be defined with metadata that specifies a
    Validator for this field. This *can* be done manually using the regular Python dataclass function `dataclasses.field()` like this:

    ```
    @dataclass
    class ExampleDataclass:
        example_field: str = field(metadata={'validator': StringValidator()})
        optional_field: str = field(default='', metadata={'validator': StringValidator()})
    ```

    To simplify (and prettify) your dataclasses, there are also some helper functions in `wtfjson.helpers.dataclasses` that generate
    this metadata for you, e.g. the decorator `@validator_dataclass` and the function `validator_field()`. It is highly recommended
    to use these helpers instead of defining the metadata manually.

    Equivalent example using the helper functions:

    ```
    @validator_dataclass
    class ExampleDataclass:
        example_field: str = StringValidator()
        optional_field: str = validator_field(StringValidator(), default='')
    ```

    All fields defined in the dataclass will be required by default. To make a field optional, define a default value (or default_factory).
    """
    dataclass_cls: type = None

    def __init__(self, dataclass_cls: Optional[type] = None):
        # For easier subclassing: If 'self.dataclass_cls' is already set (e.g. as class member in a subclass), use this as the default.
        if dataclass_cls is None:
            dataclass_cls = getattr(self, 'dataclass_cls', None)

        # Check that dataclass_cls is actually a dataclass, and that it is the class itself and not an instance of it
        if dataclass_cls is None:
            raise InvalidValidatorOptionException("Parameter 'dataclass_cls' must be specified (or set as class member in a subclass).")
        if not dataclasses.is_dataclass(dataclass_cls):
            raise InvalidValidatorOptionException("Parameter 'dataclass_cls' must be a dataclass type.")
        if not isinstance(dataclass_cls, type):
            raise InvalidValidatorOptionException("Parameter 'dataclass_cls' is a dataclass instance, but must be a dataclass type.")

        self.dataclass_cls = dataclass_cls

        # Collect field validators and required fields for the DictValidator by examining the dataclass fields
        field_validators = {}
        required_fields = []

        # Note: Pycharm falsely complains that we're calling dataclasses.fields() on something that is neither a dataclass instance nor
        # a type, even though we explicitly checked the type beforehand to ensure that it's really a dataclass type. Whatever, Pycharm...
        for dataclass_field in dataclasses.fields(dataclass_cls):
            dataclass_field: dataclasses.Field  # (Type hint)

            field_name = dataclass_field.name
            # Validators are stored in the metadata of a field by the `@validator_dataclass` decorator
            validator = dataclass_field.metadata.get('validator')

            # Check that a validator is defined and has the correct type
            if validator is None:
                raise DataclassInvalidFieldValidatorException("Dataclass field '{}' has no defined Validator.".format(field_name))
            if not isinstance(validator, Validator):
                raise DataclassInvalidFieldValidatorException(
                    "Validator specified for dataclass field '{}' is not of type 'Validator').".format(field_name))

            # Add dataclass field to the DictValidator fields
            field_validators[field_name] = validator

            # The field is optional if either a default or a default_factory is defined for it
            if dataclass_field.default is dataclasses.MISSING and dataclass_field.default_factory is dataclasses.MISSING:
                required_fields.append(field_name)

        # Initialize the underlying DictValidator
        super().__init__(field_validators=field_validators, required_fields=required_fields)

    def validate(self, input_data: Any) -> T_Dataclass:
        """
        Validate an input dictionary according to the specified dataclass. Returns an instance of the dataclass.
        """
        validated_dict = super().validate(input_data)
        return self.dataclass_cls(**validated_dict)
