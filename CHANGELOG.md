# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Unreleased

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.3.2...HEAD)

### Added

- Official support for Python 3.10.


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
