# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


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
