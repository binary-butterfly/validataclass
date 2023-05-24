"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
import inspect
import warnings
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from validataclass.dataclasses import Default, NoDefault
from validataclass.exceptions import ValidationError, DataclassValidatorFieldException, DataclassPostValidationError, \
    InvalidValidatorOptionException
from . import Validator, DictValidator

__all__ = [
    'DataclassValidator',
    'T_Dataclass',
]

# Type variable for type hints in DataclassValidator
T_Dataclass = TypeVar('T_Dataclass')


class DataclassValidator(Generic[T_Dataclass], DictValidator):
    """
    Validator that converts dictionaries to instances of user-defined dataclasses with validated fields.

    The DataclassValidator is basically a specialized variant of the DictValidator that takes a dataclass with special
    metadata as parameter, which it uses to determine the dictionary fields, which validators to use for validating
    them, which fields are required or optional, and what default values to use for optional fields. Input data is first
    validated as a regular dictionary and then used to create an instance of the dataclass.

    While you *can* define this metadata manually using the built-in Python dataclass function `dataclasses.field()`,
    it is highly recommended to use the helpers provided by this library, i.e. the decorator `@validataclass` and (if
    necessary) the function `validataclass_field()`.

    Example:

    ```
    from validataclass.dataclasses import validataclass, validataclass_field

    @validataclass
    class ExampleDataclass:
        example_field: str = StringValidator()
        optional_field: str = StringValidator(), Default('')

        # Compatibility note: In Python 3.7 parentheses are required when setting a Default using the tuple notation:
        # optional_field: str = (StringValidator(), Default(''))

        # Equivalent definition using validataclass_field():
        # example_field: str = validataclass_field(StringValidator())
        # optional_field: str = validataclass_field(StringValidator(), default='')

        # "Behind the scenes": Equivalent definition using plain dataclass fields:
        # example_field: str = field(metadata={'validator': StringValidator()})
        # optional_field: str = field(metadata={'validator': StringValidator(), 'default': Default('')})
    ```

    Note: You can define required and optional fields in any order. This differs from regular dataclasses where by
    default all required fields must be defined first, followed by all optional fields. See chapter 5 (Validation with
    Dataclasses) in the library documentation for more details about this.

    All fields that do NOT specify a default value (or explicitly use the special value `NoDefault`) are required.

    Post-validation checks can be implemented in the dataclass either using the `__post_init__()` special method (which
    is part of regular dataclasses and thus also works without validataclass) or using a `__post_validate__()` method
    (which is called by the DataclassValidator after creating the object). The latter also supports *context-sensitive*
    validation, which means you can pass extra arguments to the `validate()` call that will be passed both to all field
    validators and to the `__post_validate__()` method (as long as it is defined to accept the keyword arguments).

    In post-validation you can either raise regular `ValidationError` exceptions, which will be automatically wrapped
    inside a `DataclassPostValidationError` exception, or raise such an exception directly (in which case you can
    also specify errors for individual fields, which provides more precise errors to the user).

    Here is an example for such a `__post_validate__()` method that also happens to be context-sensitive:

    ```
    @validataclass
    class ExampleDataclass:
        optional_field: str = StringValidator(), Default('')

        def __post_validate__(self, *, require_optional_field: bool = False):
            if require_optional_field and not self.optional_field:
                raise DataclassPostValidationError(field_errors={
                    'value': RequiredValueError(reason='The optional field is required for some reason.'),
                })
    ```

    In this example, the field "optional_field" is usually optional, but there are cases where you need the field to be
    set, which is only determined at runtime, i.e. when calling the validate() method of DataclassValidator. For this
    you can now set the context argument `require_optional_field` (as defined in the `__post_validate__` method):

    ```
    validator = DataclassValidator(ExampleDataclass)
    obj = validator.validate(input_data, require_optional_field=True)
    ```
    """

    # Dataclass type that the validated dictionary will be converted to
    dataclass_cls: Type[T_Dataclass] = None

    # Field default values
    field_defaults: Dict[str, Default] = None

    def __init__(self, dataclass_cls: Optional[Type[T_Dataclass]] = None) -> None:
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

        self.dataclass_cls = dataclass_cls  # noqa (PyCharm thinks the type is incompatible, which is nonsense)
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

            # Make field optional if a default value is set
            if field_default is NoDefault:
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

    def _pre_validate(self, input_data: Any, **kwargs) -> dict:
        """
        Pre-validation steps: Validates the input as a dictionary and fills in the default values.
        """
        # Validate raw dictionary using underlying DictValidator
        validated_dict = super().validate(input_data, **kwargs)

        # Fill optional fields with default values
        for field_name, field_default in self.field_defaults.items():
            if field_name not in validated_dict:
                validated_dict[field_name] = field_default.get_value()

        return validated_dict

    def validate(self, input_data: Any, **kwargs) -> T_Dataclass:
        """
        Validate an input dictionary according to the specified dataclass. Returns an instance of the dataclass.
        """
        # Pre-validate the raw dictionary and fill in default values
        validated_dict = self._pre_validate(input_data, **kwargs)

        # Try to create dataclass object from validated dictionary and catch exceptions that may be raised in post-validation
        try:
            validated_object = self.dataclass_cls(**validated_dict)
            return self._post_validate(validated_object, **kwargs)
        except DataclassPostValidationError as error:
            # Error already has correct exception type, just reraise
            raise error
        except ValidationError as error:
            # Wrap validation error in a DataclassPostValidationError
            raise DataclassPostValidationError(error=error)
        # Ignore all non-ValidationError exceptions (these are either errors in the code or should be handled properly by the user)

    @staticmethod
    def _post_validate(validated_object: T_Dataclass, **kwargs) -> T_Dataclass:
        """
        Post-validation steps: Calls the `__post_validate__()` method on the dataclass object (if it is defined).
        """
        # Post validation using the custom __post_validate__() method in the dataclass (if defined)
        if hasattr(validated_object, '__post_validate__'):
            post_validate_spec = inspect.getfullargspec(validated_object.__post_validate__)

            # Warn about __post_validate__() with positional arguments (ignoring "self")
            if len(post_validate_spec.args) > 1 or post_validate_spec.varargs:
                warnings.warn(
                    f'{validated_object.__class__.__name__}.__post_validate__() is defined with positional arguments. '
                    'This should still work, but it is recommended to use keyword-only arguments instead.'
                )

            # If __post_validate__() accepts arbitrary keyword arguments (**kwargs), we can just pass all keyword
            # arguments to the function. Otherwise we need to filter out all keys that are not accepted as keyword
            # arguments by the function.
            if post_validate_spec.varkw is not None:
                context_kwargs = kwargs
            else:
                context_kwargs = {
                    key: value for key, value in kwargs.items()
                    if key in post_validate_spec.kwonlyargs + post_validate_spec.args
                }

            validated_object.__post_validate__(**context_kwargs)

        return validated_object
