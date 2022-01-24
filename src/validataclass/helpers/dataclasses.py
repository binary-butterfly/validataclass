"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
from collections import namedtuple
from typing import Any, Union, Dict, Optional

from validataclass.exceptions import DataclassValidatorFieldException
from validataclass.validators import Validator
from .dataclass_defaults import Default, NoDefault

# Specify which functions/symbols are imported with `from module import *`
__all__ = [
    'validataclass',
    'validataclass_field',
]

# Internal types
_ValidatorField = namedtuple('_ValidatorField', ['validator', 'default'])


# Internal functions

def _prepare_dataclass_metadata(cls) -> None:
    """
    Prepares a soon-to-be dataclass (before it is decorated with @dataclass) to be usable with DataclassValidator by checking it
    for Validator objects and setting dataclass metadata.

    (Used internally by the @validataclass decorator.)
    """
    # In case of a subclassed validataclass, get the already existing fields
    existing_validator_fields = _get_existing_validator_fields(cls)

    # Get class annotations
    cls_annotations = cls.__dict__.get('__annotations__', {})

    # Check for fields/attributes that have validators defined but missing a type annotation (most likely an error)
    for name, value in cls.__dict__.items():
        # Skip attributes with leading underscores, and attributes that have type annotations
        if name[0] == '_' or name in cls_annotations:
            continue

        # Check if attribute has a validator and/or default object (as single value or as part of a tuple)
        value_tuple = value if isinstance(value, tuple) else (value,)
        if any(isinstance(v, (Validator, Default)) for v in value_tuple):
            raise DataclassValidatorFieldException(
                f'Dataclass field "{name}" has a defined Validator and/or Default object, but no type annotation.')

    # Prepare dataclass fields by checking for validators and setting metadata accordingly
    for name, field_type in cls_annotations.items():
        value = getattr(cls, name, None)

        # InitVars currently do not work, so better raise an Exception right here to avoid confusing error messages
        if field_type is dataclasses.InitVar or type(field_type) is dataclasses.InitVar:
            raise DataclassValidatorFieldException(f'Dataclass field "{name}": InitVars currently not supported by DataclassValidator.')

        # Skip field if it is already a dataclass Field object (created by field() or validataclass_field())
        if isinstance(value, dataclasses.Field):
            continue

        # Parse field value to a named tuple with a validator and a default object
        try:
            (field_validator, field_default) = _parse_validator_tuple(value)
        except Exception as e:
            raise DataclassValidatorFieldException(f'Dataclass field "{name}": {e}')

        # If the field is already existing in a superclass and has a validator and/or default, overwrite them with new values
        if name in existing_validator_fields:
            existing_field = existing_validator_fields.get(name)
            if field_validator is None:
                field_validator = existing_field.validator
            if field_default is None:
                field_default = existing_field.default

        # Ensure that a validator is set, as well as a default (defaulting to NoDefault)
        if not isinstance(field_validator, Validator):
            raise DataclassValidatorFieldException(f'Dataclass field "{name}" must specify a Validator.')
        if not isinstance(field_default, Default):
            field_default = NoDefault

        # Create dataclass field
        setattr(cls, name, validataclass_field(validator=field_validator, default=field_default))


def _get_existing_validator_fields(cls) -> Dict[str, _ValidatorField]:
    """
    Returns a dictionary containing all fields (as `_ValidatorField` objects) of an existing validataclass that have a validator set in
    their metadata, or an empty dictionary if the class is not a dataclass (yet).

    (Internal helper function.)
    """
    if not dataclasses.is_dataclass(cls):
        return {}

    validator_fields = {}

    for field in dataclasses.fields(cls):
        # Ignore fields that don't have a validator in their metadata
        if field.metadata and 'validator' in field.metadata:
            validator_fields[field.name] = _ValidatorField(
                validator=field.metadata.get('validator'),
                default=field.metadata.get('validator_default', NoDefault),
            )

    return validator_fields


def _parse_validator_tuple(args: Union[tuple, None, Validator, Default]) -> _ValidatorField:
    """
    Parses field arguments (the value of a field in not yet decorated dataclass) to a tuple of a Validator and a Default object.

    (Internal helper function.)
    """
    # Ensure args is a tuple
    if args is None:
        args = ()
    elif not isinstance(args, tuple):
        args = (args,)

    # Currently a field can only have two arguments (a validator and/or a Default object)
    if len(args) > 2:
        raise ValueError('Unexpected number of arguments.')

    # Find validator and default objects in argument tuple and create a named tuple from it
    arg_validator = None
    arg_default = None

    for arg in args:
        if isinstance(arg, Validator):
            if arg_validator is not None:
                raise ValueError('Only one Validator can be specified.')
            arg_validator = arg
        elif isinstance(arg, Default):
            if arg_default is not None:
                raise ValueError('Only one Default can be specified.')
            arg_default = arg
        else:
            raise TypeError('Unexpected type of argument: ' + type(arg).__name__)

    return _ValidatorField(validator=arg_validator, default=arg_default)


# Extend Python dataclass functions for usage with DataclassValidator

def validataclass(cls=None, **kwargs):
    """
    Decorator that turns a normal class into a DataclassValidator-compatible dataclass.

    Prepares the class by generating dataclass metadata that is needed by the DataclassValidator, then turns the class into a dataclass
    using the regular @dataclass decorator.

    Dataclass fields can be defined by specifying a `Validator` object and optionally a `Default` object (comma-separated as a tuple),
    or by using `validataclass_field()` or `dataclasses.field()`.

    For an attribute to be recognized as a dataclass field, the attribute needs to have a type annotation (e.g. `foo: int = ...`). The
    decorator will raise an error if it detects a field that has a defined validator but no type annotation (unless the attribute's name
    begins with an underscore, e.g. `_foo = IntegerValidator()` would not raise an error, but would NOT result in a datafield either).

    Example:

    ```
    @validataclass
    class ExampleDataclass:
        # Explicit field creation:
        example_field: str = validataclass_field(StringValidator(), default='not set')
        post_init_field: int = field(init=False, default=0)

        # Implicit field creation:
        another_field: str = StringValidator()
        field_with_default: str = StringValidator(), Default('not set')

        # Compatibility note: In Python 3.7 parentheses are required when setting a Default using the tuple notation:
        # field_with_default: str = (StringValidator(), Default('not set'))
    ```

    Note: As of now, InitVars are not supported because they are not recognized as proper fields. This might change in a future version.
    As a workaround you can specify normal fields that you can access in __post_init__() and use as a init variable. The only difference
    to real InitVars is that this field will still exist after initialization.

    Optional parameters will be passed to the `@dataclass` decorator. In most cases no parameters are necessary.
    """

    def wrap(_cls):
        _prepare_dataclass_metadata(_cls)
        return dataclasses.dataclass(_cls, **kwargs)

    # Check if decorator is called as @validataclass or @validataclass(**kwargs)
    if cls is None:
        # With parenthesis (and optional keyword arguments)
        return wrap

    # Called as @validataclass without arguments
    return wrap(cls)


def validataclass_field(validator: Validator, default: Any = NoDefault, *, metadata: Optional[dict] = None, **kwargs):
    """
    Define a dataclass field compatible with DataclassValidator.

    Wraps the regular `dataclasses.field()` function, but has special parameters to add validator metadata to the field.

    Additional keyword arguments will be passed to `dataclasses.field()`, with some exceptions:
    - 'default' is handled by this function and is *not* passed on (default values are handled differently than in normal dataclasses)
    - 'default_factory' is not allowed (use `default=DefaultFactory(...)` instead)
    - 'init' is not allowed (validators wouldn't be applied with init=False; to create a non-init field, use a normal `field(init=False)`)

    Parameters:
        validator: Validator to use for validating the field (saved as metadata)
        default: Default value to use when the field does not exist in the input data (preferably a `Default` object)
        metadata: Base dictionary for field metadata, gets merged with the metadata generated by this function
        **kwargs: Additional keyword arguments that are passed to `dataclasses.field()`
    """
    # If metadata is specified as argument, use it as the base for the field's metadata
    if metadata is None:
        metadata = {}

    # Check for incompatible keyword arguments
    if 'init' in kwargs:
        raise ValueError('Keyword argument "init" is not allowed in validator field.')
    if 'default_factory' in kwargs:
        raise ValueError('Keyword argument "default_factory" is not allowed in validator field (use default=DefaultFactory(...) instead).')

    # Add validator metadata
    metadata['validator'] = validator

    # Add default values to metadata
    if default is not NoDefault and default is not dataclasses.MISSING:
        # Allow raw values as default parameter by autocreating Default objects from them
        metadata['validator_default'] = default if isinstance(default, Default) else Default(default)

    # Create a dataclass field with our metadata
    return dataclasses.field(metadata=metadata, **kwargs)
