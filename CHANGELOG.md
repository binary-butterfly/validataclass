# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.9.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.9.0) - 2023-05-24

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.8.1...0.9.0)

This release adds official support for Python for Workgroups 3.11, as well as some minor changes.

### Added

- `EmailValidator`: Add parameter `to_lowercase`. [#106]

### Changed

- Allow defining `__post_validate__()` with specific context arguments without `**kwargs`. [#105]

### Fixed

- Fix Python 3.11 incompatibilities due to `UnsetValue` not being hashable. [#102]
- Also fix missing `__hash__` methods in the `Default` classes (for completeness). [#102]

### Testing / CI

- Update GitHub actions to fix deprecation warnings. [#103]
- Update local test environment for tox 4. [#104]

[#102]: https://github.com/binary-butterfly/validataclass/pull/102
[#103]: https://github.com/binary-butterfly/validataclass/pull/103
[#104]: https://github.com/binary-butterfly/validataclass/pull/104
[#105]: https://github.com/binary-butterfly/validataclass/pull/105
[#106]: https://github.com/binary-butterfly/validataclass/pull/106


## [0.8.1](https://github.com/binary-butterfly/validataclass/releases/tag/0.8.1) - 2022-11-30

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.8.0...0.8.1)

### Fixed

- `AnyOfValidator` and `EnumValidator`: Fixed wrong default value. Now the validators are really case-insensitive by default.


## [0.8.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.8.0) - 2022-11-30

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.7.2...0.8.0)

This release adds two new validators and a handful of new parameters to existing validators.

It also introduces two **breaking changes**, which in practice shouldn't really affect anyone negatively, and one
**deprecation** of an existing validator parameter. See the changes below.

### Added

- `AllowEmptyString`: New wrapper validator that accepts empty strings (by [@TomasHalgas]). [#91]
- `DiscardValidator`: New validator that discards any input and always returns a predefined value. [#94]
- `EmailValidator` and `RegexValidator`: Add parameter `allow_empty` to allow empty strings (by [@TomasHalgas]). [#89]
- `EmailValidator`: Add parameter `max_length`. [#97]
- `DecimalValidator`: Add parameter `rounding` to specify rounding mode (with a new default, see "Changed"). [#99]

### Changed

- **Breaking change:** `AnyOfValidator` and `EnumValidator` are now **case-sensitive** by default. [#98]
  - The parameter `case_insensitive` is **replaced** with a new parameter `case_sensitive` which defaults to False.
  - The old parameter is still supported for compatibility, but is now deprecated and will be removed in a future version.
  - If you have set `case_insensitive=True` before, you can simply remove this parameter now as this is the default now.
- **Breaking change:** `DecimalValidator` (and all subclasses) now uses `decimal.ROUND_HALF_UP` as default rounding mode. [#99]
  - Until now, the rounding mode of the current decimal context was used, which defaults to `decimal.ROUND_HALF_EVEN`.
  - Use the `rounding` parameter to change this. To restore the old behavior and use the decimal context, set `rounding=None`.

### Deprecated

- `AnyOfValidator` and `EnumValidator`: The parameter `case_insensitive` is now deprecated and will be removed in a future
  version. (See "Changed" above.) [#98]

### Testing

- Fix version incompatibility in test suite. [#95]
- `AnyOfValidator`: Add unit tests with an empty list for allowed values. [#96]

### New contributors

- [@TomasHalgas] made their first contributions in [#89] and [#91].

[#89]: https://github.com/binary-butterfly/validataclass/pull/89
[#91]: https://github.com/binary-butterfly/validataclass/pull/91
[#94]: https://github.com/binary-butterfly/validataclass/pull/94
[#95]: https://github.com/binary-butterfly/validataclass/pull/95
[#96]: https://github.com/binary-butterfly/validataclass/pull/96
[#97]: https://github.com/binary-butterfly/validataclass/pull/97
[#98]: https://github.com/binary-butterfly/validataclass/pull/98
[#99]: https://github.com/binary-butterfly/validataclass/pull/99

[@TomasHalgas]: https://github.com/TomasHalgas


## [0.7.2](https://github.com/binary-butterfly/validataclass/releases/tag/0.7.2) - 2022-09-26

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.7.1...0.7.2)

This patch fix a bug with the type hinting for `@validataclass` and `DataclassValidator` introduced in 0.7.1.

### Fixed

- Fixed typehints of `@validataclass` decorator. Auto-deduction in `DataclassValidator` should work now. [#85]

[#85]: https://github.com/binary-butterfly/validataclass/pull/85


## [0.7.1](https://github.com/binary-butterfly/validataclass/releases/tag/0.7.1) - 2022-09-26

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.7.0...0.7.1)

This small patch release improves type hinting for the `@validataclass` decorator and the `DataclassValidation`.

### Changed

- `DataclassValidator`: The exact type of the validator (e.g. `DataclassValidator[MyDataclass]`) and thus the return
  type of `validate()` is now auto-deduced from the constructor arguments without an explicit type annotation. [#84]
- The `@validataclass` decorator has (hopefully correct) type annotations now. [#84]

[#84]: https://github.com/binary-butterfly/validataclass/pull/84


## [0.7.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.7.0) - 2022-09-22

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.6.2...0.7.0)

This release mainly introduces **context-sensitive (post-)validation**. There are some more additions planned for this
feature (e.g. dependencies between dataclass fields), but for now we have a solid base.

It also features a handful of smaller additions and changes, see below.

There is a potential **breaking change** (which probably won't affect anybody), and a sort of **deprecation** that
**will** affect most custom validators in the future, so make sure to upgrade your validators as explained below.

### Added

- Basic support for **context-sensitive validation**. [#77]
  - All built-in validators now support arbitrary keyword arguments (so called **context arguments**) in the `validate()`
    method. These can be used to change the behavior of a validator at validation time based on some kind of application
    context. Most validators don't do anything with them except passing them down to child validators (e.g. to the item
    validators in a `ListValidator`, etc.), but you can implement custom validators that use them.
  - To keep compatibility with custom validators that do not accept context arguments yet, a **provisional** helper
    method `validate_with_context()` was added to the base `Validator` class. This method simply calls the `validate()`
    method, but checks whether it supports context arguments. If yes, context arguments are passed to `validate()`,
    else `validate()` is called without any extra arguments. This method will become obsolete and eventually removed in
    the future, and should only be used in cases where it is unsure whether a validator supports context arguments.
- Context-sensitive **post-validation in dataclasses**. [#77]
  - The `DataclassValidator` will now call the method `__post_validate__()` on your dataclass instances if you have
    defined this method. Additionally, if the method accepts arbitrary keyword arguments (i.e. `**kwargs`, although the
    name of this parameter doesn't matter), all context arguments will be passed to it.
  - You can use this to implement context-sensitive post-validation. For example, if you implement a `PATCH` endpoint in
    a REST API, you could have fields that are sometimes optional and sometimes required, depending on a property of the
    object the user wants to update. You can now fetch the object before calling `validate()`, then pass the object (or
    just the property) as a context argument to `validate()`, and then access it in `__post_validate__()` to implement a
    context-sensitive field requirement check.
  - The `__post_init__()` method of regular dataclasses can still be used for post-validation as before. It cannot be
    used context-sensitively, though, because we cannot pass arbitrary keyword arguments to it.
- `DateTimeValidator`: Add parameter `discard_milliseconds` to discard the milli- and microseconds of datetimes. [#79]
- `AnyOfValidator` and `EnumValidator`: Add parameter `case_insensitive` for case-insensitive string matching. [#81]
- New helper function `unset_to_none()` (returns `None` if value is `UnsetValue`). [#76]

### Changed

- All built-in validators now support context arguments in the `validate()` method. See above. [#77]
- The `validate()` method of the `DataclassValidator` was restructured a bit for easier extendability. (This may be
  subject of additional changes in the future, though.) [#77]
- The `@validataclass` decorator is now marked as a "data class transform" using the `@dataclass_transform` decorator
  as specified in [PEP 681](https://peps.python.org/pep-0681/). [#78]
  - Since this decorator was only introduced in Python 3.11, we use the [typing-extensions](https://pypi.org/project/typing-extensions/)
    library which backports new typing features like this.
- `ListValidator` and `EnumValidator` are now defined as generic classes for better type hinting. [#80]
- `AnyOfValidator` and `EnumValidator` now accept `allowed_values` and `allowed_types` as any iterable. [#80]
- `AnyOfValidator` and `EnumValidator`: The `ValueNotAllowedError` now lists all allowed values (unless they are more than 20). [#81]

### Deprecated

- Validator classes that do not accept context arguments are now deprecated. [#77]
  - When defining a `Validator` subclass, the `__init_subclass__()` method will check whether your `validate()` method
    accepts arbitrary keyword arguments. If not, a `DeprecationWarning` will be issued.
  - Existing custom validators will keep working for now, but this compatibility will be removed in version 1.0.
  - To update your custom validators, simply add `**kwargs` to the parameter list of `validate()`. If your validator
    class is based on an existing validator, make sure to pass the context arguments down to the `validate()` of your
    base class as well, i.e. `super().validate(input_data, **kwargs)`.

### Removed

- **Breaking change:** The `post_validate()` method of the `DataclassValidator` was **removed**. [#77]
  - (This should not to be confused with the new `__post_validate__()`, however, which is a method of dataclasses, not
    of the validator itself.)
  - This method was removed because a) post-validation using either `__post_init__()` or the new `__post_validate__()`
    method in the dataclass should be preferred, b) the validator was restructured in a way that makes this method
    redundant, and c) it was probably never used anyway.
  - If you do need post-validation as part of a subclassed `DataclassValidator`, you can extend either `validate()` or
    the new `_post_validate()` private method (but make sure to extend, not override it, since it also handles the call
    of the dataclass's `__post_validate__()` method).

[#76]: https://github.com/binary-butterfly/validataclass/pull/76
[#77]: https://github.com/binary-butterfly/validataclass/pull/77
[#78]: https://github.com/binary-butterfly/validataclass/pull/78
[#79]: https://github.com/binary-butterfly/validataclass/pull/79
[#80]: https://github.com/binary-butterfly/validataclass/pull/80
[#81]: https://github.com/binary-butterfly/validataclass/pull/81


## [0.6.2](https://github.com/binary-butterfly/validataclass/releases/tag/0.6.2) - 2022-07-11

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.6.1...0.6.2)

This release fixes a bug with multiple inheritance in validataclasses.

### Fixed

- Fix overriding of existing field properties in validataclasses with multiple inheritance. [#71]

[#71]: https://github.com/binary-butterfly/validataclass/pull/71


## [0.6.1](https://github.com/binary-butterfly/validataclass/releases/tag/0.6.1) - 2022-06-16

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.6.0...0.6.1)

This release fixes a **critical bug** introduced in 0.6.0.

### Added

- `Default` objects now support equality comparison (implemented `__eq__`). [#69]

### Fixed

- Fix `Default` objects with mutable values (e.g. lists). [#69]

[#69]: https://github.com/binary-butterfly/validataclass/pull/69


## [0.6.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.6.0) - 2022-06-15

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.5.0...0.6.0)

This release features a reimplementation of field defaults in validataclasses (for details, see [#63] and [#65]), a bit
of code restructuring and a new parameter for the `RegexValidator`.

There is a potential **breaking change** and multiple **deprecations**.


### Added

- `RegexValidator`: Add parameter `output_template` to generate output strings from a template (by [@lahdjirayhan]). [#61]

### Changed

- Reimplementation of field defaults in validataclasses to be more consistent with regular dataclasses. [#65]
  - Optional validataclass fields now have proper dataclass default values (additionally to the validataclass-specific
    `Default` objects).
  - This means that validataclasses can now be instantiated in the same way as regular dataclasses, without the need of
    the `ValidataclassMixin.create_with_defaults()` class method.
  - In Python 3.10 and higher, the new dataclass flag `kw_only=True` is used to allow for required and optional fields
    to be defined in any order. In older Python versions, a workaround is used instead (every required field will have
    a `default_factory` that raises an exception if the field is omitted).
  - **Breaking change:** Due to the `kw_only=True` flag, instantiating validataclass objects using positional arguments
    (e.g. `MyDataclass(42, 'foo')` is not supported anymore, starting with Python 3.10. It's recommended to use keyword
    arguments instead (e.g. `MyDataclass(foo=42, bar='foo')`).
- Moved all dataclass related helpers from `validataclass.helpers` to separate modules in `validataclass.dataclasses`. [#66]
  - **Please adjust your imports.** Importing from the old location **will** stop working in a future version.
  - Affected are: The `validataclass` decorator, `validataclass_field()`, `ValidataclassMixin`, `Default`, `DefaultFactory`,
    `DefaultUnset` and `NoDefault`.
  - To find all imports that need adjustment, search your code for `validataclass.helpers`. The old imports will emit
    deprecation warnings now, so it might also help to enable deprecation warnings.
- The CI pipeline will now fail if the code coverage sinks below 100%. [#65]

### Deprecated

- `ValidataclassMixin`: The `create_with_defaults()` class method is now deprecated as it is no longer needed. [#65]
  - To create an instance of a validataclass, you can now simply use the regular dataclass constructor, e.g.
    `MyDataclass(foo=42, ...)` instead of `MyDataclass.create_with_defaults(foo=42, ...)`.
- Importing dataclass related helpers from `validataclass.helpers` is now deprecated since they have moved (see above). [#66]

[#61]: https://github.com/binary-butterfly/validataclass/pull/61
[#63]: https://github.com/binary-butterfly/validataclass/issues/63
[#65]: https://github.com/binary-butterfly/validataclass/pull/65
[#66]: https://github.com/binary-butterfly/validataclass/pull/66


## [0.5.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.5.0) - 2022-05-12

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.4.0...0.5.0)

This release introduces some new validators, new parameters for existing validators and some other smaller changes.

There are two potentially **breaking changes** ([#51] and [#59]), although it's very unlikely that any existing code is
negatively affected by it.

### Added

- `AnythingValidator`: New validator that accepts any input without validation. [#56]
- `RejectValidator`: New validator that rejects any input. [#55]
- `NoneToUnsetValue`: New validator as a shortcut for `Noneable(..., default=UnsetValue)`. [#57]
- `ListValidator`: Add parameter `discard_invalid` to ignore invalid list elements (by [@lahdjirayhan]). [#43]
- `UrlValidator`: Add parameters `allow_empty` and `max_length` (by [@lahdjirayhan]).  [#49]
- `RegexValidator`: Add parameter `custom_error_class` to set a custom exception class. [#54]

### Changed

- `IntegerValidator`: Set defaults for `min_value` and `max_value` to restrict input to 32-bit integers. [#51]
- `Noneable`: Raise exception if wrapped validator is not a valid `Validator` object. [#52]
- `DecimalValidator`: Allow `min_value` and `max_value` parameters to be specified as integers. [#53]
- `DataclassValidator`: Don't wrap uncaught exceptions in `InternalValidationError` anymore. [#59]

### Removed

- Removed `InternalValidationError` exception. [#59]

### Fixed

- **GitHub CI:** Fix running unit test workflows in pull requests from forked repositories. [#45], [#47], [#48]

### New contributors

- [@lahdjirayhan] made their first contributions in [#43] and [#49].

[#43]: https://github.com/binary-butterfly/validataclass/pull/43
[#45]: https://github.com/binary-butterfly/validataclass/pull/45
[#47]: https://github.com/binary-butterfly/validataclass/pull/47
[#48]: https://github.com/binary-butterfly/validataclass/pull/48
[#49]: https://github.com/binary-butterfly/validataclass/pull/49
[#51]: https://github.com/binary-butterfly/validataclass/pull/51
[#52]: https://github.com/binary-butterfly/validataclass/pull/52
[#53]: https://github.com/binary-butterfly/validataclass/pull/53
[#54]: https://github.com/binary-butterfly/validataclass/pull/54
[#55]: https://github.com/binary-butterfly/validataclass/pull/55
[#56]: https://github.com/binary-butterfly/validataclass/pull/56
[#57]: https://github.com/binary-butterfly/validataclass/pull/57
[#59]: https://github.com/binary-butterfly/validataclass/pull/59

[@lahdjirayhan]: https://github.com/lahdjirayhan


## [0.4.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.4.0) - 2022-02-01

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.3.2...0.4.0)

### Added

- Official support for Python 3.10. [#30]
- `IntegerValidator`: Add optional boolean parameter `allow_strings` to accept integer strings as input (e.g. `"123"`). [#31]
- `FloatValidator`: Add optional boolean parameter `allow_integers`. [#32]
- `FloatToDecimalValidator`: Add optional boolean parameters `allow_integers` and `allow_strings`. Also, minimum and
  maximum values can now be specified as floats, integers, `Decimal` or decimal strings. [#32]
- `NumericValidator`: New validator as shortcut for `FloatToDecimalValidator` with `allow_integers` and `allow_strings`. [#33]
- `StringValidator`: Added some unit tests for strings with unicode characters (including emoji). [#34]

### Changed

- `FloatToDecimalValidator`: Reimplemented validator, based on `DecimalValidator` instead of `FloatValidator`. [#33]
  - `NumberRangeError` exceptions raised by this validator now consistently use decimal strings for min/max values.

### Fixed

- Minor fixes for `Optional` type hints. [#30]
- Add missing export for `T_Dataclass` in package `validataclass.validators`. [#30]

[#30]: https://github.com/binary-butterfly/validataclass/pull/30
[#31]: https://github.com/binary-butterfly/validataclass/pull/31
[#32]: https://github.com/binary-butterfly/validataclass/pull/32
[#33]: https://github.com/binary-butterfly/validataclass/pull/33
[#34]: https://github.com/binary-butterfly/validataclass/pull/34


## [0.3.2](https://github.com/binary-butterfly/validataclass/releases/tag/0.3.2) - 2021-11-11

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.3.1...0.3.2)

### Changed

- `ValidataclassMixin`: The `to_dict()` method now removes UnsetValues from the dictionary, unless the optional parameter
  `keep_unset_values=True` is set. [#28](https://github.com/binary-butterfly/validataclass/pull/28)


## [0.3.1](https://github.com/binary-butterfly/validataclass/releases/tag/0.3.1) - 2021-11-11

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.3.0...0.3.1)

### Changed

- `@validataclass` decorator detects fields with validator but without type annotations and will raise errors about that now.
  [#27](https://github.com/binary-butterfly/validataclass/pull/27)

### Fixed

- `@validataclass` allows empty dataclasses now (raised an AttributeError before).
  [#27](https://github.com/binary-butterfly/validataclass/pull/27)


## [0.3.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.3.0) - 2021-11-10

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.2.0...0.3.0)

### Added

- Support for class inheritance of validataclasses, e.g. extend an existing validataclass by adding new fields setting different default
  values for existing fields. [#11](https://github.com/binary-butterfly/validataclass/pull/11)
- Type aliases `OptionalUnset[T]` and `OptionalUnsetNone[T]`. [#12](https://github.com/binary-butterfly/validataclass/pull/12)
- Mixin class `ValidataclassMixin` with methods `to_dict()` and `create_with_defaults()`.
  [#13](https://github.com/binary-butterfly/validataclass/pull/13)

### Changed

- Tuples for specifying field validators and defaults in a validataclass can now be in any order, so `(default, validator)` instead
  of `(validator, default)` is allowed now. (Side effect of [#11](https://github.com/binary-butterfly/validataclass/pull/11))

### Fixed

- Fix link to docs in README.md to make link work on PyPI. [#8](https://github.com/binary-butterfly/validataclass/pull/8)


## [0.2.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.2.0) - 2021-10-25

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.1.0...0.2.0)

### Added

- Initial version of [documentation](docs/index.md). [#6](https://github.com/binary-butterfly/validataclass/pull/6)
- Added changelog file. [#7](https://github.com/binary-butterfly/validataclass/pull/7)

### Changed

- `DefaultUnset` is now a sentinel object instead of a class. [#4](https://github.com/binary-butterfly/validataclass/pull/4)

### Fixed

- Value in `Default` class is now deepcopied on retrieval. [#3](https://github.com/binary-butterfly/validataclass/pull/3)
- Typesafe comparisons of integers and booleans in `AnyOfValidator`. [#5](https://github.com/binary-butterfly/validataclass/pull/5)


## [0.1.0](https://github.com/binary-butterfly/validataclass/releases/tag/0.1.0) - 2021-10-07

[Full changelog](https://github.com/binary-butterfly/validataclass/commits/0.1.0)

### General

- Initial release.
- Full rewrite of previous library [wtfjson](https://github.com/binary-butterfly/wtfjson) from scratch.
- Rename to **validataclass**.
- Automated unit testing with 100% code coverage.
- Automated publishing on [PyPI](https://pypi.org/project/validataclass/).

### Added

- Added first validators:
  - Basic type validators: `BooleanValidator`, `IntegerValidator`, `FloatValidator`, `StringValidator`
  - Decimal validators: `DecimalValidator`, `FloatToDecimalValidator`
  - Choice validators: `AnyOfValidator`, `EnumValidator`
  - Date and time validators: `DateValidator`, `TimeValidator`, `DateTimeValidator`
  - Extended string validators: `RegexValidator`, `EmailValidator`, `UrlValidator`
  - Meta validators: `Noneable`
  - Composite type validators: `ListValidator`, `DictValidator`
- Implemented dataclass support:
  - Validator: `DataclassValidator`
  - Helper functions: `validataclass_field()`, `@validataclass`
  - Default classes: `Default`, `DefaultFactory`, `DefaultUnset`

### Known issues

- No documentation yet (will follow in 0.2.0).
