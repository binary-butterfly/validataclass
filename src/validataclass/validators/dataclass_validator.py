"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
import inspect
import warnings
from typing import Any, Dict, Generic, Optional, Type, TypeVar, TYPE_CHECKING

from typing_extensions import TypeGuard

from validataclass.dataclasses import Default, NoDefault
from validataclass.exceptions import (
    DataclassInvalidPreValidateSignatureException,
    DataclassPostValidationError,
    DataclassValidatorFieldException,
    InvalidValidatorOptionException,
    ValidationError,
)
from .dict_validator import DictValidator
from .validator import Validator

__all__ = [
    'DataclassValidator',
    'T_Dataclass',
]

# Type variable for an instance of a dataclass
T_Dataclass = TypeVar('T_Dataclass', bound=object)

# Define type alias for dataclasses.Field
# NOTE: In Python >= 3.9, dataclasses.Field is a Generic, so mypy will complain if no type parameter is given.
# However, Field[Any] will raise a runtime error in Python 3.8 because there the type is not parametrized yet.
# TODO: Replace type alias with dataclasses.Field[Any] when removing Python 3.9 support. (#15)
if TYPE_CHECKING:
    T_DataclassField = dataclasses.Field[Any]
else:
    T_DataclassField = dataclasses.Field


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

    Pre-validation preprocessing (e.g. to map fields to different names) can be implemented in the dataclass by defining
    the `__pre_validate__()` class method or static method. This method is called by the DataclassValidator before
    validating the input data. It must accept the input dictionary as a positional argument and return a dictionary that
    will then replace the input dictionary and be validated. See documentation for an example.

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
    dataclass_cls: Type[T_Dataclass]

    # Field default values
    field_defaults: Dict[str, Default]

    def __init__(self, dataclass_cls: Optional[Type[T_Dataclass]] = None) -> None:
        # For easier subclassing: If 'self.dataclass_cls' is already set (e.g. as class member in a subclass), use that
        # class as the default.
        if dataclass_cls is None:
            dataclass_cls = getattr(self, 'dataclass_cls', None)

        # Ensure that dataclass_cls is either given as a parameter or predefined in a subclass
        if dataclass_cls is None:
            raise InvalidValidatorOptionException(
                'Parameter "dataclass_cls" must be specified (or set as class member in a subclass).'
            )

        # Check that dataclass_cls is actually a dataclass, and that it is the class itself and not an instance of it
        if not _is_dataclass_type(dataclass_cls):
            raise InvalidValidatorOptionException('Parameter "dataclass_cls" must be a dataclass type.')

        self.dataclass_cls = dataclass_cls
        self.field_defaults = {}

        # Collect field validators and required fields for the DictValidator by examining the dataclass fields
        field_validators = {}
        required_fields = []

        for field in dataclasses.fields(dataclass_cls):
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
    def _get_field_validator(field: T_DataclassField) -> Validator:
        # Parse field metadata to get Validator
        validator = field.metadata.get('validator')

        # Ensure that validator is defined and has a valid type
        if validator is None:
            raise DataclassValidatorFieldException(f'Dataclass field "{field.name}" has no defined Validator.')
        if not isinstance(validator, Validator):
            raise DataclassValidatorFieldException(
                f'Validator specified for dataclass field "{field.name}" is not of type "Validator".'
            )

        return validator

    @staticmethod
    def _get_field_default(field: T_DataclassField) -> Default:
        # Parse field metadata to get Default object
        default = field.metadata.get('validator_default', NoDefault)

        # Default is optional
        if default is NoDefault or default is None:
            return NoDefault

        # Ensure valid type
        if not isinstance(default, Default):
            raise DataclassValidatorFieldException(
                f'Default specified for dataclass field "{field.name}" is not of type "Default".'
            )

        return default

    def _pre_validate(self, input_data: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Pre-validation steps: Validates the input as a dictionary and fills in the default values.
        """
        # Custom pre-validation using the __pre_validate__() method (class or static) in the dataclass (if defined)
        pre_validate_func = getattr(self.dataclass_cls, '__pre_validate__', None)
        if pre_validate_func is not None:
            # Ensure type before calling the DictValidator to make sure __pre_validate__ gets a dict
            self._ensure_type(input_data, dict)

            # Inspect the __pre_validate__() method
            pre_validate_spec = inspect.getfullargspec(pre_validate_func)
            pre_validate_expected_arg_count = 2 if inspect.ismethod(pre_validate_func) else 1

            # Ensure __pre_validate__() has exactly one positional arguments (input_data), or two if it is a class
            # method (cls, input_data)
            if len(pre_validate_spec.args) != pre_validate_expected_arg_count or pre_validate_spec.varargs:
                raise DataclassInvalidPreValidateSignatureException(
                    f'{self.dataclass_cls.__name__}.__pre_validate__() must have exactly one positional argument'
                    ' (not counting the class object if it is a class method).'
                )

            # If __pre_validate__() accepts arbitrary keyword arguments (**kwargs), we can just pass all keyword
            # arguments to the function. Otherwise we need to filter out all keys that are not accepted as keyword
            # arguments by the function.
            if pre_validate_spec.varkw is not None:
                context_kwargs = kwargs
            else:
                context_kwargs = {
                    key: value for key, value in kwargs.items()
                    if key in pre_validate_spec.kwonlyargs
                }

            # Filter input dictionary through __pre_validate__()
            input_data = pre_validate_func(input_data, **context_kwargs)

        # Validate raw dictionary using underlying DictValidator
        validated_dict = super().validate(input_data, **kwargs)

        # Fill optional fields with default values
        for field_name, field_default in self.field_defaults.items():
            if field_name not in validated_dict:
                validated_dict[field_name] = field_default.get_value()

        return validated_dict

    def validate(self, input_data: Any, **kwargs: Any) -> T_Dataclass:  # type: ignore[override]
        """
        Validate an input dictionary according to the specified dataclass. Returns an instance of the dataclass.
        """
        # Pre-validate the raw dictionary and fill in default values
        validated_dict = self._pre_validate(input_data, **kwargs)

        # Try to create dataclass object from validated dict and catch exceptions that may be raised in post-validation
        try:
            validated_object = self.dataclass_cls(**validated_dict)
            return self._post_validate(validated_object, **kwargs)
        except DataclassPostValidationError as error:
            # Error already has correct exception type, just reraise
            raise error
        except ValidationError as error:
            # Wrap validation error in a DataclassPostValidationError
            raise DataclassPostValidationError(error=error)
        # Ignore all non-ValidationError exceptions (these are either errors in the code or should be handled properly
        # by the user)

    @staticmethod
    def _post_validate(validated_object: T_Dataclass, **kwargs: Any) -> T_Dataclass:
        """
        Post-validation steps: Calls the `__post_validate__()` method on the dataclass object (if it is defined).
        """
        # Custom post-validation using the __post_validate__() method in the dataclass (if defined)
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


def _is_dataclass_type(obj: Any) -> TypeGuard[Type[T_Dataclass]]:
    """
    Type-safe helper function that checks if the given object is a dataclass (specifically a class, not an instance).
    """
    return dataclasses.is_dataclass(obj) and isinstance(obj, type)
