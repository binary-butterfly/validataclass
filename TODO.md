# To Do

## Before 1.0.0 release

Things that are required before releasing the version 1.0.0.

- Change library name ("validataclass"?)
- Implement EmailValidator and UrlValidator
- Write documentation
- Code polishing, e.g. unify docstring formatting (when to use which types of quotes, etc.)
- Better packaging, release on PyPI, automatically updating version numbers
- Automated unit testing via CI pipelines


## New features

Features or feature ideas that might be added someday:

- Dataclasses/dicts: Field constraints (e.g. "if field A is true/defined, then field B is required")
- Dataclass inheritance/patching: Reduce code duplication when having multiple dataclasses that are mostly identical (e.g.
  a `UserCreateInput` dataclass where all/most fields are required, and a `UserPatchInput` dataclass which is an extended version of
  the first dataclass, making fields from the first one optional and adding additional fields), e.g. using dataclass inheritance and a
  new `validator_patch_dataclass` decorator
- Multi-validators:
  - Validator chains (pipe result of validator A to validator B (filters) or use the first non-exception result (fallback chain)) 
  - Multi-type validators (use validator A for integer input, validator B for string input, ...)
- RegexValidator: Parameter 'output_template': if set, return `match.expand(output_template)` instead of unmodified string
  (or create a subclass, like RegexReplaceValidator/RegexTemplateValidator)
- EnumValidator: Option to use enum member names instead of their values (e.g. input string 'FOO' results in `SomeEnum.FOO`)


## Code modernizations when raising minimum required Python version

Currently the minimum required version of Python is 3.7, which lacks some features that would improve the code a bit.

Things to improve when raising the minimum required version of Python:

- (3.8+) Dataclass defaults: Assigning tuples without parentheses to fields with type annotations (in examples and unit tests),
  e.g. `foo: int = (IntegerValidator(), Default(0))` to `foo: int = IntegerValidator(), Default(0)`
- (3.8+) `validator_dataclass` decorator: positional-arguments-only operator: `def validator_dataclass(cls=None, /, **kwargs):`
- (3.9+) Collection type hints with built-in types (list, dict, set), e.g. replace `typing.List[str]` with `list[str]`
- (3.9+) DateTimeValidator timezones: Use new module [zoneinfo](https://docs.python.org/3/library/zoneinfo.html) (in examples and tests)
