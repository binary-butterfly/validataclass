# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.0] - 2021-10-25

[Full changelog](https://github.com/binary-butterfly/validataclass/compare/0.1.0...0.2.0)

### Added

- Initial version of [documentation](docs/index.md) ([#6](https://github.com/binary-butterfly/validataclass/pull/6))
- Added changelog file

### Changed

- `DefaultUnset` is now a sentinel object instead of a class ([#4](https://github.com/binary-butterfly/validataclass/pull/4))

### Fixed

- Value in `Default` class is now deepcopied on retrieval ([#3](https://github.com/binary-butterfly/validataclass/pull/3))
- Typesafe comparisons of integers and booleans in `AnyOfValidator` ([#5](https://github.com/binary-butterfly/validataclass/pull/5))


## [0.1.0] - 2021-10-07

[Full changelog](https://github.com/binary-butterfly/validataclass/commits/0.1.0)

### General

- Initial release
- Full rewrite of previous library [wtfjson](https://github.com/binary-butterfly/wtfjson) from scratch
- Rename to **validataclass**
- Automated unit testing with 100% code coverage
- Automated publishing on [PyPI](https://pypi.org/project/validataclass/)

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

- No documentation yet (will follow in 0.2.0)


[Unreleased]: https://github.com/binary-butterfly/validataclass/compare/0.1.0...HEAD
[0.2.0]: https://github.com/binary-butterfly/validataclass/releases/tag/0.2.0
[0.1.0]: https://github.com/binary-butterfly/validataclass/releases/tag/0.1.0
