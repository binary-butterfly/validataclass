# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import dataclasses
from typing import Any

from wtfjson.exceptions import DataclassValidatorFieldException
from wtfjson.validators import Validator
from .dataclass_defaults import Default, NoDefault

# Specify which functions/symbols are imported with `from module import *`
__all__ = [
    'validator_dataclass',
    'validator_field',
]


# Internal functions

def _prepare_dataclass_metadata(cls: type) -> None:
    """
    Prepares a soon-to-be dataclass (before it is decorated with @dataclass) to be usable with DataclassValidator by checking it
    for Validator objects and setting dataclass metadata.

    (Used internally by the @validator_dataclass decorator.)
    """
    for name, field_type in cls.__annotations__.items():
        value = getattr(cls, name, None)
        arguments = []

        # InitVars currently do not work, so better raise an Exception right here to avoid confusing error messages
        if field_type is dataclasses.InitVar or type(field_type) is dataclasses.InitVar:
            raise DataclassValidatorFieldException(f'Dataclass field "{name}": InitVars currently not supported by DataclassValidator.')

        # Skip field if it is already a dataclass Field object (created by field() or validator_field())
        if isinstance(value, dataclasses.Field):
            continue

        # In case of tuples, extract the first element
        if isinstance(value, tuple):
            value, *arguments = value

        # Every field that was not already defined using field() must have a Validator
        if not isinstance(value, Validator):
            raise DataclassValidatorFieldException(f'Dataclass field "{name}" must specify a Validator.')

        # Currently a field can only have one extra argument (an optional Default object)
        if len(arguments) > 1:
            raise DataclassValidatorFieldException(f'Dataclass field "{name}": Unexpected number of arguments.')

        default = arguments[0] if arguments else NoDefault
        if not isinstance(default, Default):
            raise DataclassValidatorFieldException(f'Dataclass field "{name}": Unexpected type of argument (expected Default).')

        # Create dataclass field
        setattr(cls, name, validator_field(validator=value, default=default))


# Extend Python dataclass functions for usage with DataclassValidator

def validator_dataclass(cls=None, **kwargs):
    """
    Decorator that turns a normal class into a DataclassValidator-compatible dataclass.

    Prepares the class by generating dataclass metadata that is needed by the DataclassValidator, then turns the class into a dataclass
    using the regular @dataclass decorator.

    Dataclass fields can be created either explicitly using `validator_field()` or `dataclasses.field()`, or implicitly by specifying
    a `Validator` object and optionally a `Default` object (comma-separated as a tuple).

    Example:

    ```
    @validator_dataclass
    class ExampleDataclass:
        # Explicit field creation:
        example_field: str = validator_field(StringValidator(), default='not set')
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

    # Check if decorator is called as @validator_dataclass or @validator_dataclass(**kwargs)
    if cls is None:
        # With parenthesis (and optional keyword arguments)
        return wrap

    # Called as @validator_dataclass without arguments
    return wrap(cls)


def validator_field(validator: Validator, default: Any = NoDefault, *, metadata: dict = None, **kwargs):
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
