"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import dataclasses
import sys
from collections import namedtuple
from typing import Union, Dict

from validataclass.exceptions import DataclassValidatorFieldException
from validataclass.validators import Validator
from .defaults import Default, NoDefault
from .validataclass_field import validataclass_field

__all__ = [
    'validataclass',
]

# Internal types
_ValidatorField = namedtuple('_ValidatorField', ['validator', 'default'])


def validataclass(cls=None, **kwargs):
    """
    Decorator that turns a normal class into a DataclassValidator-compatible dataclass.

    Prepares the class by generating dataclass metadata that is needed by the DataclassValidator, then turns the class
    into a dataclass using the regular @dataclass decorator.

    Dataclass fields can be defined by specifying a `Validator` object and optionally a `Default` object (comma-separated
    as a tuple), or by using `validataclass_field()` or `dataclasses.field()`.

    For an attribute to be recognized as a dataclass field, the attribute must have a type annotation (e.g. `foo: int = ...`).
    The decorator will raise an error if it detects a field that has a defined validator but no type annotation (unless
    the attribute's name begins with an underscore, e.g. `_foo = IntegerValidator()` would not raise an error, but would
    NOT result in a datafield either).

    Example:

    ```
    @validataclass
    class ExampleDataclass:
        # Implicit field definitions (using validators only or tuples)
        example_field1: str = StringValidator()  # This field is required because it has no default
        example_field2: str = StringValidator(), Default('not set')  # This field is optional

        # Field definitions using validataclass_field() and regular dataclasses field()
        example_field3: str = validataclass_field(StringValidator())  # Same as example_field1
        example_field4: str = validataclass_field(StringValidator(), default='not set')  # Same as example_field2
        post_init_field: int = field(init=False, default=0)  # Post-init field without validator

        # COMPATIBILITY NOTE: In Python 3.7 parentheses are required when setting a Default using the tuple notation:
        # field_with_default: str = (StringValidator(), Default('not set'))
    ```

    Note: As of now, InitVars are not supported because they are not recognized as proper fields. This might change in a
    future version. As a workaround you can specify normal fields that you can access in __post_init__() and use as init
    variables. The only difference to real InitVars is that this field will still exist after initialization.

    Optional parameters to the decorator will be passed directly to the `@dataclass` decorator. In most cases no
    parameters are necessary. In Python 3.10 and upwards, the argument `kw_only=True` will be used by default.
    """

    # In Python 3.10 and higher, we use kw_only=True by default to allow for required and optional fields in any order.
    # In older Python versions, we use a workaround by setting default_factory to a function that raises an exception
    # for required fields.
    if sys.version_info >= (3, 10):  # pragma: ignore-py-lt-310
        kwargs.setdefault('kw_only', True)
    else:  # pragma: ignore-py-gte-310
        pass

    def wrap(_cls):
        _prepare_dataclass_metadata(_cls)
        return dataclasses.dataclass(_cls, **kwargs)  # noqa (weird PyCharm warning)

    # Check if decorator is called as @validataclass or @validataclass(**kwargs)
    if cls is None:
        # With parenthesis (and optional keyword arguments)
        return wrap

    # Called as @validataclass without arguments
    return wrap(cls)


def _prepare_dataclass_metadata(cls) -> None:
    """
    Prepares a soon-to-be dataclass (before it is decorated with @dataclass) to be usable with DataclassValidator by
    checking it for Validator objects and setting dataclass metadata.

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

        # Create dataclass field (_name is only needed for generating the default_factory for required fields in Python < 3.10)
        setattr(cls, name, validataclass_field(validator=field_validator, default=field_default, _name=name))


def _get_existing_validator_fields(cls) -> Dict[str, _ValidatorField]:
    """
    Returns a dictionary containing all fields (as `_ValidatorField` objects) of an existing validataclass that have a
    validator set in their metadata, or an empty dictionary if the class is not a dataclass (yet).

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
