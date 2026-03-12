# 7. Type checking with mypy

## What's the problem?

Due to the way the library is designed, type checkers have a hard time with validataclasses.

For example, if we have a typical validataclass definition like this...

```python
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import IntegerValidator

@validataclass
class ExampleDataclass:
    field1: int = IntegerValidator()
    field2: int | None = IntegerValidator(), Default(None)
```

... type checkers will point out that the assignments in this class are incorrect.

Because from the perspective of a type checker, this class doesn't make a lot of sense. We're assigning an object of
type `IntegerValidator` to `field1`, which is typed as `int` - but a validator is not an integer. It gets even worse
with field `field2` where we're assigning a tuple consisting of two seemingly random objects to an `int | None` field.
A `tuple[IntegerValidator, Default[None]]` is neither an `int` nor `None`.

Of course at runtime, the class is still correct, because the `@validataclass` decorator transforms the class and its
weird assignments to a simple dataclass and stores the validataclass-specific information in metadata.

Type checkers like mypy and pyright cannot know what the decorator does (except that the decorators are dataclass-like
transformers since they're decorated with `typing.dataclass_transform` - but sadly that's not enough here).

However, mypy has a plugin system exactly for this purpose. This is very specific to mypy, though, so if you want to use
a different type checker than mypy, I'm afraid you're out of luck.


## How to use the mypy plugin

The mypy plugin is included in the library, you only need to enable it in your mypy configuration.

If you're using a `pyproject.toml` file (which is the recommended way nowadays to configure Python projects and tools),
this is an example for a mypy configuration:

```toml
[tool.mypy]
# These lines are just an example and might not be needed or need to be adjusted in your project:
files = ["src/"]
mypy_path = "src/"
explicit_package_bases = true

# This is the important part:
plugins = ["validataclass.mypy.plugin"]
```


### Advanced plugin configuration

There are some advanced settings for configuring the plugin itself. The plugin configuration currently only supports
`pyproject.toml` and should be defined in the section `[tool.validataclass_mypy]`.

The configuration is expected to be in the same `pyproject.toml` file that is used to configure mypy. The plugin does
not have any discovery mechanisms for config files, it simply looks up which config file was read by mypy during
initialization, and if it's a `.toml` file, it reads the same file to get its configuration.

#### Strictness / optional rules

- `allow_incompatible_field_overrides` (bool, default `true`): Allow incompatible overrides of fields in validataclass
  sub classes, i.e. changing the type of an existing field in a sub class. This is enabled by default because it is a
  common use case to define sub classes where, for example, only the defaults are changed. The default might be changed
  in a future version, so it's advisable to set this explicitly to true if you need it.

#### Extensions

The following settings can be used to enable support for custom extensions of the library, for example if you've
defined your own decorator that extends `@validataclass` or you're using another library that does this.

All these settings require fully qualified names, e.g. `example.module.my_custom_decorator`.

- `custom_validataclass_decorators` (list of strings): Custom decorators for creating validataclasses. 
  - These are basically treated as aliases to `@validataclass`, so their signature and behaviour should be compatible to
    the original decorator.
  - They are also required to be decorated with `@typing.dataclass_transform(kw_only_default=True)`.
- `custom_field_functions` (list of strings): Custom functions that create validataclass fields.
  - These must have the a compatible signature to the built-in `validataclass_field()` function, e.g. they must accept
    a validator (as the only positional argument or as a named argument `validator`).
- `ignore_custom_types_in_fields` (list of strings): Custom base classes that are ignored when analyzing a field tuple.
  - By default, only instances of `Validator` or `BaseDefault` are valid types in a field definition. Other types will
    be reported as errors. With this option, you can have custom objects that get ignored by the plugin.
  - Keep in mind that the `@validataclass` decorator will still reject those objects at runtime. This option only makes
    sense in combination with a custom decorator, see `custom_validataclass_decorators`.
  - All subclasses of classes in this list will be ignored as well.

#### Miscellaneous

- `debug_mode` (bool, default `false`): If enabled, the plugin prints verbose logs. Intended for plugin debugging only.


### Error codes

The plugin defines its own mypy error codes which can be disabled or ignored in the same way as the built-in error codes
(e.g. via config or for individual lines with `# type: ignore[CODE]`.

Keep in mind that these are only for checks that are implemented by the plugin itself. Other errors, like assignments
of a wrong validator to a field, are still reported by mypy using its own error codes (e.g. `assignment`).

All error codes are sub codes of `validataclass`, so disabling `validataclass` will disable the others as well.

- `validataclass`: Various errors in field definitions, e.g. a missing or duplicate validator, an invalid type of object
  in a field tuple and more.
- `validataclass-decorator`: Incorrectly defined custom decorator (see `custom_validataclass_decorators` in config)
- `validataclass-empty-type`: Field that has an empty type, i.e. the dataclass can never be validated because the
  validator and default don't allow any value. This can happen when you're using a `RejectValidator` without a default.
  The validator will reject every input, but without a default the field is still required.
- `validataclass-not-implemented`: Special error code for edge cases that are currently not supported by the plugin.
  If you get this error, you found an edge case that was unknown to the developers. Please create a bug report for this
  to help with the plugin development. Even if you believe it was a mistake on your part, you might have found a way to
  cause an edge case that we thought can never happen.


## Common mistakes / migration guide

### Incompatible return type in custom validators

validataclass is designed with extensibility in mind: You can easily write your own validators or extend existing ones
to build on their existing functionality.

A common use case for this are validators that accept input of a basic type (like strings) and convert them to objects.
Examples of built-in validators are the `DecimalValidator` or `DateValidator`: They use the `StringValidator` for the
first step to validate input as a valid string, then they try to create a `Decimal` or `date` object from that string.

Before validataclass 0.12, the common way to do that was to inherit from a base validator (e.g. the `StringValidator`)
and extend its `validate()` method. See the following example:

```python
from datetime import date
from typing import Any, override
from validataclass.exceptions import ValidationError
from validataclass.validators import StringValidator

class DateValidator(StringValidator):
    def __init__(self) -> None:
        # Initialize base validator with some parameters
        super().__init__(min_length=1, max_length=10)

    @override
    def validate(self, input_data: Any, **kwargs: Any) -> date:
        # Use base validator to validate input as a string
        date_string = super().validate(input_data, **kwargs)

        try:
            # Convert string to a date object
            return date.fromisoformat(date_string)
        except ValueError:
            raise ValidationError(code='invalid_date')
```

This works as intended at runtime, but type checkers will complain about the return type of the `validate()` method:

```
error: Return type "date" of "validate" incompatible with return type "str" in supertype
  "validataclass.validators.string_validator.StringValidator"  [override]
```

The reason for this is called the Liskov substitution principle (LSP): Basically, if you override a method in a
subclass, the return type of the method must be the same or a subtype of the return type in the base class. The
`StringValidator` returns a `str`, but `date` is not a subtype of `str`.

Luckily, the solution to this problem is really simple in the case of our validators: Composition over inheritance.
Instead of subclassing the `StringValidator`, you can create an instance of `StringValidator` within your custom
validator (that is solely based on the abstract base class `Validator`) and use it as a helper in your validate method:

```python
from datetime import date
from typing import Any, override
from validataclass.exceptions import ValidationError
from validataclass.validators import StringValidator, Validator

class DateValidator(Validator[date]):  # Note the type parameter here
    # Base validator for validating strings
    string_validator: StringValidator

    def __init__(self) -> None:
        # Initialize string validator with some parameters
        self.string_validator = StringValidator(min_length=1, max_length=10)

    @override
    def validate(self, input_data: Any, **kwargs: Any) -> date:
        # Use string validator to validate input as a string
        date_string = self.string_validator.validate(input_data, **kwargs)

        try:
            # Convert string to a date object
            return date.fromisoformat(date_string)
        except ValueError:
            raise ValidationError(code='invalid_date')
```

Now from a typing perspective, the `DateValidator` is simply a `Validator[date]`, i.e. a validator that returns a `date`
object. It just outsources the first part of the validation to a different validator to reuse its functionality.


## How the mypy plugin works

The mypy plugin works in mysterious ways.

There is some explanation about the plugin in the description of the pull request
[!140](https://github.com/binary-butterfly/validataclass/pull/140). A more detailed explanation in the docs will follow
at some point in the future.
