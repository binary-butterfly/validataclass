# 3. Basic Validators

In this chapter we will give an overview of the different types of validator classes that are included in this library.

This chapter will focus on validators that work with **scalar** (or **single value**) input data, for example different types of strings
(including datetime strings or URLs) and numbers. We will call those **basic validators** for now.

In the [next chapter](04-lists-and-dicts.md) we will then learn how to use these basic validators to construct more **complex validators**
for data structures like lists and dictionaries, followed by [dataclasses](05-dataclasses.md), which basically are all just compositions
of the data types that we cover here.


## Quick overview

There are at least two ways to categorize the existing validator classes.

One distinction would be "base types" vs. "extended types": Base types are all validators that do **not** extend an existing validator,
i.e. they directly implement the `Validator` base class. Examples for base type validators would be `StringValidator`, `IntegerValidator`
and `DictValidator`. Extended types are all validators that **do** extend existing validators, e.g. `DecimalValidator` is based on
`StringValidator`.

A much more useful distinction is to categorize the validators according to their function:

- Boolean types:
  - `BooleanValidator`: Validates boolean values (`True` / `False`, optionally allowing strings `"true"` / `"false"`)

- String types:
  - `StringValidator`: Validates strings (with optional length requirements; singleline or multiline strings)
  - `RegexValidator`: Validates strings using a user-defined regular expression
  - `EmailValidator`: Validates email addresses
  - `UrlValidators`: Validates URLs

- Numeric types:
  - `IntegerValidator`: Validates integers (as `int`, not as `str`)
  - `FloatValidator`: Validates floats (as `float`, not as `str`)
  - `DecimalValidator`: Validates decimal **strings** (e.g. `"1.23"`) to `decimal.decimal` **objects**
  - `FloatToDecimalValidator`: Validates **floats** (e.g. `1.23`) to `decimal.decimal` **objects**

- Date and time types:
  - `DateValidator`: Validates date **strings** (e.g. `"2021-12-31"`) to `datetime.date` **objects**
  - `TimeValidator`: Validates time **strings** (e.g. `"12:34:56"`) to `datetime.time` **objects**
  - `DateTimeValidator`: Validates datetime **strings** (e.g. `"2021-12-31T12:34:56"`) to `datetime.datetime` **objects**

- Choice types:
  - `AnyOfValidator`: Only allows a user-defined set of values (any type, returned unmodified)
  - `EnumValidator`: Only allows values from a user-defined `Enum` class (returns a member of the `Enum`)

- Composite types:
  - `ListValidator`: Validates **lists**, validating each list item with a specified **item validator**
  - `DictValidator`: Validates **dicts**, validating each field with specified **field validators**
  - `DataclassValidator`: Validates **dicts** to dataclasses, using **field validators** that are defined in the dataclass

- Meta validators:
  - `Noneable`: Wraps another validator but allows the input to be `None`


These are a lot of different validators (and there will be even more in future versions) and many of them have a lot of parameters, so we
will not cover all of them here in detail.

Instead, we want to give you an idea of which validators to use for which use cases. All of the validators and their parameters are
well documented with docstrings in the code, also the code is intended to be as readable as possible, so we encourage you to take a look
at the code for more details. (In a future version we might auto-generate a reference documentation from the code, too.)


## Boolean types

### BooleanValidator

The `BooleanValidator` validates the boolean values `True` and `False`.

By default only input data of type `bool` is accepted. Optionally the parameter `allow_strings=True` can be set to also allow the strings
`"true"` and `"false"` (case-insensitive), which will then be converted to the real boolean values `True` and `False`.

**Examples:**

```python
from validataclass.validators import BooleanValidator

# Default options: Only allows boolean values
validator = BooleanValidator()
validator.validate(True)    # will return True (bool)
validator.validate(False)   # will return False (bool)
validator.validate("true")  # will raise InvalidTypeError(expected_type='bool')

# Optional parameter: Also allow strings "true" and "false"
validator = BooleanValidator(allow_strings=True)
validator.validate(True)     # will return True (bool)
validator.validate("true")   # will return True (bool, not string)
validator.validate("FALSE")  # will return False (bool, not string)
```


## String types

The following validators all have in common that they parse **strings**, which means they accept strings as input and return strings.


### StringValidator

The `StringValidator` validates arbitrary strings.

By default strings of any length are accepted (including empty strings), which can be changed with the parameters `min_length` and
`max_length`.

Also by default only "safe" singleline strings are allowed. "Safe" in this case means the strings may not contain non-printable characters
like newlines or ASCII control characters (see [`str.isprintable()`](https://docs.python.org/3/library/stdtypes.html#str.isprintable)).
This can be changed with the parameters `unsafe` and `multiline`. Please refer to the
[documentation in the code](../src/validataclass/validators/string_validator.py) for details.

**Examples:**

```python
from validataclass.validators import StringValidator

# Default options: Accepts any safe singleline string of any length
validator = StringValidator()
validator.validate("")          # will return "" (empty string)
validator.validate("banana")    # will return "banana"
validator.validate("foo\nbar")  # will raise StringInvalidCharactersError

# Length requirements: Accepts only strings with at least 1 and at most 10 characters
validator = StringValidator(min_length=1, max_length=10)
validator.validate("")              # will raise StringTooShortError
validator.validate("banana")        # will return "banana"
validator.validate("bananananana")  # will raise StringTooLongError

# Multiline option: Accepts strings with multiple lines, but no other unsafe characters
# (Line endings will be normalized to Unix style "\n" line endings)
validator = StringValidator(multiline=True)
validator.validate("foo\nbar")    # will return "foo\nbar"
validator.validate("foo\r\nbar")  # will also return "foo\nbar" (normalized line endings)
validator.validate("foo\0")       # will raise StringInvalidCharactersError

# Multiline and unsafe options: Accept *every* possible ASCII or UTF-8 character
validator = StringValidator(multiline=True, unsafe=True)
validator.validate("foo\r\nbar")  # will return "foo\r\nbar" (not normalized because unsafe=True)
validator.validate("foo\0")       # will return "foo\0" (with ASCII null-byte)
```


### RegexValidator

The `RegexValidator` uses a custom regular expression to validate strings.

The regex can be specified either as a precompiled pattern (see `re.compile()`) or as a string which will be compiled by the class.
Regex flags (e.g. `re.IGNORECASE` for case-insensitive matching) can only be set by precompiling a pattern with those flags.

The input string will then be matched against the regex using `re.fullmatch()`, which means that the **full** string must match the regex.

This validator is based on the `StringValidator` (see above) and accepts all of its parameters, so you can use `min_length`, `multiline`,
etc. just like with the `StringValidator` (the same default values are applied here).

For further information on regular expressions, see: https://docs.python.org/3/library/re.html

**Examples:**

```python
# Import Python standard library for regular expressions
import re

from validataclass.validators import RegexValidator

# This pattern accepts hexadecimal numbers with at least one hex digit
validator = RegexValidator(r'[0-9a-fA-F]+')
validator.validate("0")       # will return "0"
validator.validate("123Abc")  # will return "123Abc"
validator.validate("banana")  # will raise RegexMatchError (with code='invalid_string_format')

# Same example, but with a precompiled regex (here we can set the re.IGNORECASE flag and simplify the pattern)
validator = RegexValidator(re.compile(r'[0-9a-f]+', re.IGNORECASE))
validator.validate("123Abc")  # will return "123Abc"

# StringValidator options: Same example, but with length requirements to only allow 6-digit hex numbers (e.g. '123abc')
validator = RegexValidator(re.compile(r'[0-9a-f]+', re.IGNORECASE), min_length=6, max_length=6)
validator.validate("0")          # will raise StringTooShortError
validator.validate("123Abc")     # will return "123Abc"
validator.validate("123Abcdef")  # will raise StringTooLongError

# Same example, but setting a custom error code
validator = RegexValidator(re.compile(r'[0-9a-f]+'), custom_error_code='invalid_hex_number')
validator.validate("banana")  # will raise RegexMatchError, but with code='invalid_hex_number'
```


### EmailValidator

The `EmailValidator` validates email addresses as strings and returns them unmodified.

Please note that this validator is a bit opinionated and simplified in that it does **not** allow every email address that technically
is valid according to the RFCs. For example, it does neither allow internationalized email addresses (although this might be changed
in the future), nor oddities like quoted strings as local part or comments, because most mail software does not support those anyway
and/or might break with those adresses.

Currently this validator has no parameters.

**Example:**

```python
from validataclass.validators import EmailValidator

validator = EmailValidator()
validator.validate("foo@example.com")  # will return "foo@example.com"
validator.validate("banana")           # will return InvalidEmailError(reason='Invalid email address format.')
```


### UrlValidators

The `UrlValidator` validates URLs as strings and returns them unmodified.

Please note that this validator is a bit opinionated and simplified in that it does **not** allow every valid URL. It's intended to be
used primarily for HTTP URLs and thus only allows URLs with authority component (the `//host` part after the colon).

By default the validator allows only the URI schemes "http" and "https", requires hostnames to have a top level domain (e.g. "example.com"
but not just "example"), allows IP addresses as host, and does not allow userinfo components in the URL.

The parameters `allowed_schemes`, `require_tld`, `allow_ip` and `allow_userinfo` can be used to change these defaults.
Please refer to the [documentation in the code](../src/validataclass/validators/url_validator.py) for details.

**Examples:**

```python
from validataclass.validators import UrlValidator

# Default options: Only allows "http(s)" as scheme, requires a TLD, allows IP, does not allow userinfo
validator = UrlValidator()
validator.validate("https://example.com")                        # valid (returned unmodified)
validator.validate("http://123.45.67.89/foo")                    # valid (returned unmodified)
validator.validate("http://example.com:8080/foo?bar=baz#bloop")  # valid (returned unmodified)
validator.validate("banana")             # will raise InvalidUrlError(reason='Invalid URL format.')
validator.validate("ftp://example.com")  # will raise InvalidUrlError(reason='URL scheme is not allowed.')
validator.validate("http://localhost")   # will raise InvalidUrlError(reason='Invalid host in URL.')

# Set allowed schemes to "ftp" and "sftp" and allow userinfo components
validator = UrlValidator(allowed_schemes=['ftp', 'sftp'], allow_userinfo=True)
validator.validate("ftp://example.com/foo/bar")                     # valid (returned unmodified)
validator.validate("sftp://username:password@example.com/foo/bar")  # valid (returned unmodified)
validator.validate("https://example.com")  # will raise InvalidUrlError(reason='URL scheme is not allowed.')
```


## Numeric types

The following validators parse different types of numbers, namely **integers**, **floats** and **decimals**.

In most cases it is recommended to use either `IntegerValidator` or `DecimalValidator`. Floats are error-prone due to how binary floating
point arithmetics work, while integers and decimals are always precise.


### IntegerValidator

The `IntegerValidator` accepts integer values (as type `int`, not as strings) and returns those values unmodified.

Optionally you can specify a range of valid values using `min_value` and `max_value`.

**Examples:**

```python
from validataclass.validators import IntegerValidator

# Default: Accepts any integer
validator = IntegerValidator()
validator.validate(0)     # will return 0
validator.validate(123)   # will return 123
validator.validate(-123)  # will return -123
validator.validate("1")   # will raise InvalidTypeError (use DecimalValidator instead)

# min_value parameter: Only allow zero or positive numbers
validator = IntegerValidator(min_value=0)
validator.validate(0)     # will return 0
validator.validate(123)   # will return 123
validator.validate(-123)  # will raise NumberRangeError(min_value=0)

# min_value and max_value: Only allow values 1 to 10
validator = IntegerValidator(min_value=1, max_value=10)
validator.validate(0)   # will raise NumberRangeError(min_value=1, max_value=10)
validator.validate(1)   # will return 1
validator.validate(10)  # will return 10
validator.validate(11)  # will raise NumberRangeError(min_value=1, max_value=10)

# max_value only: Allow all values smaller than or equal to 10
validator = IntegerValidator(max_value=10)
validator.validate(1)   # will return 1
validator.validate(10)  # will return 10
validator.validate(11)  # will raise NumberRangeError(max_value=10)
# NOTE: This also allows any negative number (because no min_value is specified):
validator.validate(-1234)  # valid! will return -1234
```


### FloatValidator

The `FloatValidator` accepts float values (those of type `float`, no integers and no strings!) and returns those unmodified.

Only finite value are allowed (i.e. neither `Infinity` nor `NaN`).

Optionally you can specify a range of valid values using `min_value` and `max_value`.

**Examples:**

```python
from validataclass.validators import FloatValidator

# Default options: Accepts any finite float value
validator = FloatValidator()
validator.validate(1.234)   # will return 1.234 (as float)
validator.validate(-0.001)  # will return -0.001
validator.validate(1.0)     # will return 1.0
validator.validate(1)       # will raise InvalidTypeError (use IntegerValidator instead)
validator.validate("1.23")  # will raise InvalidTypeError (use DecimalValidator instead)

# Value range: Only allow values from -1.0 to +1.0
validator = FloatValidator(min_value=-1.0, max_value=1.0)
validator.validate(0.123)   # will return 0.123
validator.validate(-1.0)    # will return -1.0
validator.validate(1.234)   # will raise NumberRangeError(min_value=-1.0, max_value=1.0)
validator.validate(-1.234)  # will raise NumberRangeError(min_value=-1.0, max_value=1.0)
```


### DecimalValidator

The `DecimalValidator` accepts decimal numbers **as strings** (e.g. `"1.234"`) and **converts** them to
[`decimal.Decimal`](https://docs.python.org/3/library/decimal.html) objects (see Python standard library).

Only allows finite numbers in regular decimal notation (e.g. `"1.234"`, `"-42"`, `".00"`, ...), but no other values that are accepted
by `decimal.Decimal` (e.g. no `Infinity` or `NaN` and no scientific notation).

Optionally a number range (minimum/maximum decimal value), minimum/maximum number of decimal places and a fixed number of decimal
places in the output value can be specified. A fixed number of output places will result in rounding according to the current decimal
context (see `decimal.getcontext()`), by default this means that `"1.49"` will be rounded to `1` and `"1.50"` to `2`.

**Examples:**

```python
from decimal import Decimal

from validataclass.validators import DecimalValidator

# Default options: Allow any decimal value with any number of decimal places
validator = DecimalValidator()
validator.validate("1")       # will return Decimal('1')
validator.validate("1.23")    # will return Decimal('1.23')
validator.validate("-0.123")  # will return Decimal('-0.123')
validator.validate(1)         # will raise InvalidTypeError (use IntegerValidator instead)
validator.validate(1.23)      # will raise InvalidTypeError (use FloatValidator or FloatToDecimalValidator instead)

# Value range: Can be either a decimal string or a Decimal object (but no integer or float)
validator = DecimalValidator(min_value="0", max_value=Decimal("1.0"))
validator.validate("1")       # will return Decimal('1')
validator.validate("1.23")    # will raise NumberRangeError
validator.validate("-0.123")  # will raise NumberRangeError

# Decimal place requirement: Allow any value with 2, 3 or 4 decimal places
validator = DecimalValidator(min_places=2, max_places=4)
validator.validate("1.23")       # will return Decimal('1.23')
validator.validate("-0.1234")    # will return Decimal('-0.1234')
validator.validate("100000.00")  # will return Decimal('100000.00')
validator.validate("1")          # will raise DecimalPlacesError
validator.validate("0.12345")    # will raise DecimalPlacesError

# Output places: Same example as above, but the output will always have 3 decimal places (rounding if necessary)
validator = DecimalValidator(min_places=2, max_places=4, output_places=3)
validator.validate("1.23")       # will return Decimal('1.230')
validator.validate("0.1234")     # will return Decimal('0.123')
validator.validate("0.1235")     # will return Decimal('0.124')
validator.validate("100000.00")  # will return Decimal('100000.000')
```


### FloatToDecimalValidator

The `FloatToDecimalValidator` accepts **float** values (like the `FloatValidator`) but **converts** them to `Decimal` objects (like
the `DecimalValidator`).

Like the `DecimalValidator` it supports the optional parameters `min_value`, `max_value` and `output_places`. It **does not** support the
`min_places` and `max_places` parameters though (those are technically not possible with floats)!

**Note:** Due to the way that floats work, the resulting decimals can have inaccuracies! It is recommended to use `DecimalValidator`
with decimal strings instead of floats as input whenever possible. This validator mainly exists for cases where you need to accept floats
as input.

**Examples:**

```python
from validataclass.validators import FloatToDecimalValidator

# Default options: Accepts any finite float value
validator = FloatToDecimalValidator()
validator.validate(1.234)   # should return Decimal('1.234')
validator.validate(1)       # will raise InvalidTypeError (use IntegerValidator instead)
validator.validate("1.23")  # will raise InvalidTypeError (use DecimalValidator instead)

# Number range and output places: Allow values from 0 to 1, always output with 3 decimal places
validator = FloatToDecimalValidator(min_value=0, max_value=1, output_places=3)
validator.validate(0.0)     # should return Decimal('0.000')
validator.validate(0.1234)  # should return Decimal('0.123')
validator.validate(0.1235)  # should return Decimal('0.124')
validator.validate(1.0)     # should return Decimal('1.000')
```


## Date and time types

The following validators all handle different kinds of date and time input. They all accept **strings** as input and convert them to
objects from the Python standard library module [`datetime`](https://docs.python.org/3/library/datetime.html).


### DateValidator

The `DateValidator` accepts date strings in `YYYY-MM-DD` format (e.g. `"2021-01-31"`) and converts them to to `datetime.date` objects.

Currently no parameters are supported.

**Examples:**

```python
from validataclass.validators import DateValidator

validator = DateValidator()
validator.validate("2021-01-31")  # will return datetime.date(2021, 1, 31)
validator.validate("3999-12-31")  # will return datetime.date(3999, 12, 31)
validator.validate("31.01.2021")  # will raise InvalidDateError
validator.validate("2021-00-00")  # will raise InvalidDateError
validator.validate("2021-13-31")  # will raise InvalidDateError
```

### TimeValidator

The `TimeValidator` accepts time strings in `HH:MM:SS` and/or `HH:MM` format (e.g. `"13:05:59"` or `"13:05"`) and converts them to
`datetime.time` objects.

The exact format can be specified using the `TimeFormat` enum, which has the following values:

- `NO_SECONDS`: Only allows `HH:MM` strings
- `WITH_SECONDS`: Only allows `HH:MM:SS` strings (default format)
- `OPTIONAL_SECONDS`: Allows both `HH:MM:SS` and `HH:MM` strings (where `HH:MM` is equivalent to `HH:MM:00`)

**Examples:**

```python
from validataclass.validators import TimeValidator, TimeFormat

# Default format (WITH_SECONDS): Accepts only "HH:MM:SS" strings
validator = TimeValidator()
validator.validate("13:05:59")  # will return datetime.time(13, 5, 59)
validator.validate("13:05")     # will raise InvalidTimeError

# NO_SECONDS format: Accepts only "HH:MM" strings
validator = TimeValidator(TimeFormat.NO_SECONDS)
validator.validate("13:05")     # will return datetime.time(13, 5)
validator.validate("13:05:59")  # will raise InvalidTimeError

# OPTIONAL_SECONDS format: Accepts strings with and without seconds
validator = TimeValidator(TimeFormat.OPTIONAL_SECONDS)
validator.validate("13:05")     # will return datetime.time(13, 5)
validator.validate("13:05:59")  # will return datetime.time(13, 5, 59)
```


### DateTimeValidator

The `DateTimeValidator` accepts datetime strings in the ISO 8601 compatible format `YYYY-MM-DDTHH:MM:SS[.fff[fff][+HH:MM]` and converts
them to `datetime.datetime` objects. The `T` in this format stands for the literal character `T` as a separator between date and time
(e.g. `"2021-12-31T12:34:56"` or `"2021-12-31T12:34:56.123456"`).

The string may specify a timezone using `+HH:MM` or `-HH:MM`. Also the special suffix `Z` is allowed to denote UTC as the timezone
(e.g. `"2021-12-31T12:34:56Z"` which is equivalent to `"2021-12-31T12:34:56+00:00"`). If no timezone is specified, the datetime is
interpreted as local time (see also the parameter `local_timezone`).

By default the validator allows datetimes with and without timezones. To restrict this to specific formats you can use the
`DateTimeFormat` enum, which has the following values:

- `ALLOW_TIMEZONE`: Default behavior, allows datetimes with any timezone or without a timezone (local time)
- `REQUIRE_TIMEZONE`: Only allows datetimes that specify a timezone (but any timezone is allowed)
- `REQUIRE_UTC`: Only allows datetimes that explicitly specify UTC as timezone (either with `Z` or `+00:00`)
- `LOCAL_ONLY`: Only allows datetimes **without** timezone (will be interpreted as local time)
- `LOCAL_OR_UTC`: Only allows local datetimes (no timezone) or UTC datetimes (explicitly specified with `Z` or `+00:00`)


Example input               | `ALLOW_TIMEZONE` | `REQUIRE_TIMEZONE` | `REQUIRE_UTC` | `LOCAL_ONLY` | `LOCAL_OR_UTC`
----------------------------|------------------|--------------------|---------------|--------------|---------------
`2021-12-31T12:34:56`       | valid            |                    |               | valid        | valid
`2021-12-31T12:34:56Z`      | valid            | valid              | valid         |              | valid
`2021-12-31T12:34:56+00:00` | valid            | valid              | valid         |              | valid
`2021-12-31T12:34:56+02:00` | valid            | valid              |               |              |


The parameter `local_timezone` can be used to set the timezone for datetime strings that don't specify a timezone. For example, if
`local_timezone` is set to a UTC+3 timezone, the string `"2021-12-31T12:34:56"` will be treated like `"2021-12-31T12:34:56+03:00"`.
Similarly, to interpret datetimes without timezone as UTC, set `local_timezone=datetime.timezone.utc`. If `local_timezone` is not
set (which is the default), the resulting `datetime` will have no timezone info (`tzinfo=None`).

The parameter `target_timezone` can be used to convert all resulting datetime objects to a uniform timezone. This requires the
datetimes to already have a timezone, so to allow local datetimes (without timezone info in the input string) you need to specify
`local_timezone` as well.

See [`datetime.timezone`](https://docs.python.org/3/library/datetime.html#datetime.timezone) and
[`dateutil.tz`](https://dateutil.readthedocs.io/en/stable/tz.html) for information on defining timezones.

Additionally the parameter `datetime_range` can be used to specify a range of datetime values that are allowed (e.g. a minimum and
a maximum datetime, which can be dynamically defined using callables). See the classes `DateTimeRange` and `DateTimeOffsetRange`
from [`validataclass.helpers.datetime_range`](../src/validataclass/helpers/datetime_range.py) for further information.

**Note:** When using datetime ranges, make sure not to mix datetimes that have timezones with local datetimes because those comparisons
will raise `TypeError` exceptions. It's recommended either to use only datetimes with defined timezones (for both input values and
the boundaries of the datetime ranges), or to specify the `local_timezone` parameter (which will also be used to determine the
timezone of the range boundary datetimes if they do not specify timezones themselves).

**Examples:**

```python
# Use `timezone.utc` from `datetime` to specify UTC as timezone
from datetime import timezone
# Use `dateutil.tz` to easily specify timezones that are not UTC
from dateutil import tz

from validataclass.validators import DateTimeValidator, DateTimeFormat

# Default format (ALLOW_TIMEZONE): Allow datetimes with and without timezone
validator = DateTimeValidator()
validator.validate("2021-12-31T12:34:56")        # -> datetime(2021, 12, 31, 12, 34, 56)
validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56+02:00")  # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone(timedelta(seconds=7200)))
# Times with milliseconds/microseconds:
validator.validate("2021-12-31T12:34:56.123")     # -> datetime(2021, 12, 31, 12, 34, 56, 123000)
validator.validate("2021-12-31T12:34:56.123456")  # -> datetime(2021, 12, 31, 12, 34, 56, 123456)

# REQUIRE_TIMEZONE format: Only allow datetimes with specified timezone
validator = DateTimeValidator(DateTimeFormat.REQUIRE_TIMEZONE)
validator.validate("2021-12-31T12:34:56")        # raises InvalidDateTimeError
validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56+02:00")  # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone(timedelta(seconds=7200)))

# LOCAL_OR_UTC format: Only allow datetimes either without timezone or with UTC explicitly specified
validator = DateTimeValidator(DateTimeFormat.LOCAL_OR_UTC)
validator.validate("2021-12-31T12:34:56")        # -> datetime(2021, 12, 31, 12, 34, 56)
validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56+00:00")  # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56+02:00")  # raises InvalidDateTimeError

# LOCAL_OR_UTC, but with a specified local timezone (as default value for the datetime's tzinfo)
validator = DateTimeValidator(DateTimeFormat.LOCAL_OR_UTC, local_timezone=tz.gettz('Europe/Berlin'))
validator.validate("2021-12-31T12:34:56")        # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=tzfile('[...]/Europe/Berlin'))
validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56+00:00")  # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56+02:00")  # raises InvalidDateTimeError

# Allow datetimes with arbitrary timezones (using CET/CEST (+01:00/+02:00) as local timezone), but convert all datetimes to UTC
validator = DateTimeValidator(local_timezone=tz.gettz('Europe/Berlin'), target_timezone=timezone.utc)
validator.validate("2021-12-31T12:34:56")        # -> datetime(2021, 12, 31, 11, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56Z")       # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56+00:00")  # -> datetime(2021, 12, 31, 12, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56+02:00")  # -> datetime(2021, 12, 31, 10, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T12:34:56-06:00")  # -> datetime(2021, 12, 31, 18, 34, 56, tzinfo=timezone.utc)
```

**Examples with datetime ranges:**

```python
from datetime import datetime, timedelta, timezone

from validataclass.helpers import DateTimeRange, DateTimeOffsetRange
from validataclass.validators import DateTimeValidator, DateTimeFormat

# DateTimeRange: Only allow datetimes within a specified datetime range, e.g. allow all datetimes in the year 2021
validator = DateTimeValidator(DateTimeFormat.REQUIRE_TIMEZONE, target_timezone=timezone.utc, datetime_range=DateTimeRange(
    datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    datetime(2021, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
))

validator.validate("2021-01-01T00:00:00Z")       # -> datetime(2021, 1, 1, 0, 0, tzinfo=timezone.utc)
validator.validate("2021-07-28T12:34:56Z")       # -> datetime(2021, 7, 28, 12, 34, 56, tzinfo=timezone.utc)
validator.validate("2021-12-31T23:59:59Z")       # -> datetime(2021, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

# These appear to be outside of the range, but are inside when taking the timezones into account
validator.validate("2020-12-31T23:00:00-01:00")  # -> datetime(2021, 1, 1, 0, 0, tzinfo=timezone.utc)
validator.validate("2022-01-01T00:00:00+01:00")  # -> datetime(2021, 12, 31, 23, 0, tzinfo=timezone.utc)

# These will all raise DateTimeRangeError(lower_boundary='2021-01-01T00:00:00+00:00', upper_boundary='2021-12-31T23:59:59.999999+00:00')
validator.validate("2020-12-31T23:59:59Z")       # raises DateTimeRangeError
validator.validate("2022-01-01T00:00:00Z")       # raises DateTimeRangeError
validator.validate("2021-01-01T00:00:00+01:00")  # raises DateTimeRangeError
validator.validate("2021-12-31T23:59:59-01:00")  # raises DateTimeRangeError


# DateTimeOffsetRange: Specify a datetime range using a pivot datetime and two offsets (allows all datetimes "around" the pivot datetime
# plus/minus the offsets), e.g. all datetimes between pivot_datetime - 5 minutes and pivot_datetime + 10 minutes:
validator = DateTimeValidator(DateTimeFormat.REQUIRE_UTC, datetime_range=DateTimeOffsetRange(
    pivot=datetime(2021, 7, 15, 12, 30, 0, tzinfo=timezone.utc),
    offset_minus=timedelta(minutes=5),
    offset_plus=timedelta(minutes=10)
))

validator.validate("2021-07-15T12:25:00Z")  # -> datetime(2021, 7, 15, 12, 25, tzinfo=timezone.utc)
validator.validate("2021-07-15T12:30:00Z")  # -> datetime(2021, 7, 15, 12, 30, tzinfo=timezone.utc)
validator.validate("2021-07-15T12:40:00Z")  # -> datetime(2021, 7, 15, 12, 40, tzinfo=timezone.utc)

# These will all raise DateTimeRangeError(lower_boundary='2021-07-15T12:25:00+00:00', upper_boundary='2021-07-15T12:40:00+00:00')
validator.validate("2021-07-14T12:30:00Z")  # raises DateTimeRangeError (time fits, but day is out of range)
validator.validate("2021-07-15T12:24:59Z")  # raises DateTimeRangeError (one second too early)
validator.validate("2021-07-15T12:40:01Z")  # raises DateTimeRangeError (one second too late)
```

The pivot in a `DateTimeOffsetRange` can also be a callable, which will be evaluated just when the `validate()` method is called.
If the pivot is undefined, it will default to the current time (in UTC and without milliseconds).

**Example for `DateTimeOffsetRange` with the default pivot:**

```python
from datetime import timedelta
from validataclass.helpers import DateTimeOffsetRange
from validataclass.validators import DateTimeValidator, DateTimeFormat

# This example allows all datetimes in the next 7 days, but no datetimes in the past or after these 7 days:
validator = DateTimeValidator(DateTimeFormat.REQUIRE_UTC, datetime_range=DateTimeOffsetRange(
    offset_plus=timedelta(days=7)
))

# Assuming the current date and time is: 2021-10-12, 12:00:00 UTC
validator.validate("2021-10-12T12:00:00Z")  # -> datetime(2021, 10, 12, 12, 0, 0, tzinfo=timezone.utc)
validator.validate("2021-10-15T01:23:45Z")  # -> datetime(2021, 10, 15, 1, 23, 45, tzinfo=timezone.utc)
validator.validate("2021-10-19T11:59:59Z")  # -> datetime(2021, 10, 19, 11, 59, 59, tzinfo=timezone.utc)

# These will all raise DateTimeRangeError(lower_boundary='2021-10-12T12:00:00+00:00', upper_boundary='2021-10-19T12:00:00+00:00')
validator.validate("2021-10-12T11:59:59Z")  # raises DateTimeRangeError (one second in the past)
validator.validate("2021-10-19T12:00:01Z")  # raises DateTimeRangeError (one second too late)
validator.validate("2021-10-20T12:00:00Z")  # raises DateTimeRangeError (one day too late)

# Also, the time is evaluated when validate() is called, so after waiting at least one second, the following will fail:
validator.validate("2021-10-12T12:00:00Z")  # raises DateTimeRangeError (boundaries in exception will have changed too)
```


## Choice types

A "choice type" validator accepts only values from a custom **predefined list of values**.

These values can potentially be of any type, although strings and integers are probably the most useful types here.


### AnyOfValidator

The `AnyOfValidator` is defined with a simple list of allowed values and accepts only values that are part of this list.
The values will be returned unmodified.

The list of allowed values may contain mixed types (e.g. `['banana', 123, True, None]`).

Like most other validators, the validator will first check the type of input data and will raise an `InvalidTypeError` for types that
are not allowed. Those allowed types will be automatically determined from the list of values by default (e.g. with `['foo', 'bar', 'baz']`
only strings will be accepted, while the mixed type example from above will accept all of `str`, `int`, `bool` and `NoneType`).

Optionally the allowed types can be explicitly specified using the parameter `allowed_types`.

**Examples:**

```python
from validataclass.validators import AnyOfValidator

# Accept a specific list of strings
validator = AnyOfValidator(['apple', 'banana', 'strawberry'])
validator.validate('banana')      # will return 'banana'
validator.validate('strawberry')  # will return 'strawberry'
validator.validate('pineapple')   # will raise ValueNotAllowedError()
validator.validate(1)             # will raise InvalidTypeError(expected_type='str')

# Accept a list of values of mixed types
validator = AnyOfValidator(['banana', 123, True, None])
validator.validate('banana')  # will return 'banana'
validator.validate(123)       # will return 123
validator.validate(True)      # will return True
validator.validate(None)      # will return None
# Allowed types but not allowed values:
validator.validate(3)         # will raise ValueNotAllowedError
validator.validate(False)     # will raise ValueNotAllowedError
# Not allowed type:
validator.validate(1.2)       # will raise InvalidTypeError(expected_types=['bool', 'int', 'none', 'str'])

# Explicitly specify allowed types
validator = AnyOfValidator(['banana', 123], allowed_types=int)
validator.validate(123)       # will return 123
validator.validate('banana')  # will raise InvalidTypeError(expected_type='int')
```


### EnumValidator

The `EnumValidator` is an extended `AnyOfValidator` that uses `Enum` classes instead of a simple list of allowed values.

It accepts the **values** of the Enum and converts the input value to the according enum **member**.

By default all values in the Enum are accepted as input. This can be optionally restricted by specifying the `allowed_values`
parameter, which will override the list of allowed values. Values in this list that are not valid for the Enum will be silently
ignored though.

The types allowed for input data will be automatically determined from the allowed Enum values by default, unless explicitly
specified with the parameter `allowed_types`.

**Examples:**

```python
from enum import Enum

from validataclass.validators import EnumValidator

# Define an Enum class with string values
class ExampleStringEnum(Enum):
    APPLE = 'apple'
    BANANA = 'banana'
    STRAWBERRY = 'strawberry'

# Define an Enum class with integer values
class ExampleIntegerEnum(Enum):
    FOO = 1
    BAR = 3
    BAZ = -20

# Default: Accept all values of the ExampleStringEnum
validator = EnumValidator(ExampleStringEnum)
validator.validate('apple')       # will return ExampleStringEnum.APPLE
validator.validate('banana')      # will return ExampleStringEnum.BANANA
validator.validate('strawberry')  # will return ExampleStringEnum.STRAWBERRY
validator.validate('pineapple')   # will raise ValueNotAllowedError
validator.validate(123)           # will raise InvalidTypeError(expected_type='str')

# Default: Accept all values of the ExampleIntegerEnum
validator = EnumValidator(ExampleIntegerEnum)
validator.validate(1)      # will return ExampleIntegerEnum.FOO
validator.validate(3)      # will return ExampleIntegerEnum.BAR
validator.validate(-20)    # will return ExampleIntegerEnum.BAZ
validator.validate(123)    # will raise ValueNotAllowedError
validator.validate('FOO')  # will raise InvalidTypeError(expected_type='str')

# Restrict allowed values
validator = EnumValidator(ExampleStringEnum, allowed_values=['apple', 'banana', 'pineapple'])
validator.validate('apple')       # will return ExampleStringEnum.APPLE
validator.validate('banana')      # will return ExampleStringEnum.BANANA
validator.validate('strawberry')  # will raise ValueNotAllowedError
validator.validate('pineapple')   # will raise ValueNotAllowedError (value is not defined in the Enum)

# Restrict allowed values using the Enum instead of strings
validator = EnumValidator(ExampleStringEnum, allowed_values=[ExampleStringEnum.APPLE, ExampleStringEnum.BANANA])
validator.validate('apple')       # will return ExampleStringEnum.APPLE
validator.validate('banana')      # will return ExampleStringEnum.BANANA
validator.validate('strawberry')  # will raise ValueNotAllowedError
```


## Composite types

A "composite type" validator parses **data structures** that consist of one or more scalar values or other (nested) data structures,
and validates the individual elements of these data structures using other predefined validators.

Currently two types of **input** data structures are supported: **Lists** and **dictionaries**. Additionally to those, there is also
support for [**dataclasses**](https://docs.python.org/3/library/dataclasses.html) as **output** data structures.

- **Lists** can be validated using the `ListValidator` and a specified **item validator**. The `ListValidator` will first check that
  the input is actually a list, and then validate each **item** of the list with the specified item validator. The result will be a list
  of validated items (i.e. the output of the item validator for each item).

- **Dictionaries** can be validated using the `DictValidator` and one or more specified **field validators**. The `DictValidator` will
  first check that the input is actually a dictionary, and then validate each **field** of the dictionary with the specified field
  validators (mapping the dictionary keys to validators). The result will be a dictionary with validated fields.

- **Dictionaries** can also be validated using the `DataclassValidator` and a specified **dataclass**. The dataclass must be defined
  in a special way, where each field of the dataclass has an associated **field validator**. The dictionary will first be validated
  using a `DictValidator` and then converted to an object of the dataclass.

As these validators are a bit more complex than those that we've seen before, we have dedicated the next two chapters to
[lists and dictionaries](04-lists-and-dicts.md) and [dataclasses](05-dataclasses.md).

But before we go on with them, we have another special type of validators left.


## Meta validators

Meta validators are a special category of validators. They don't validate anything on their own, instead they wrap one or more other
validators and then "decide" which one to use for a given input value (or whether to validate it at all), e.g. by looking at the type
of the input data.

Currently only the `Noneable` meta validator exists, but more are planned to be added in a future version.


### Noneable

The `Noneable` meta validator wraps another validator and additionally allows `None` as an input value.

Most validators do not allow `None` as the input value and raise an `RequiredValueError` instead. To allow a value to be `None`, the
`Noneable` meta validator can be used.

It first checks if the input value is `None`, in which case it will simply return `None`. In all other cases the input will be passed
to the wrapped validator as if it was used without `Noneable`.

Optionally a custom default value can be specified with the `default` parameter. If set, the `Noneable` validator will return this
default value instead of `None` when the input value is `None`.

Additionally, if the wrapped validator raises an `InvalidTypeError`, the meta validator will add `"none"` to the `expected_types`
parameter of the exception.

**Examples:**

```python
from validataclass.validators import Noneable, StringValidator

# Wrap a StringValidator: Accepts all strings allowed by the StringValidator but additionally allows None
validator = Noneable(StringValidator())
validator.validate('banana')  # will return the string 'banana'
validator.validate('')        # will return the string ''
validator.validate(None)      # will return None (not a string!)

# Wrap a StringValidator, but with a custom default value for None
validator = Noneable(StringValidator(), default='no value given!')
validator.validate('banana')  # will return the string 'banana'
validator.validate('')        # will return the string ''
validator.validate(None)      # will return the string 'no value given!'
```


## Summary

We have seen a lot of different types of validators now and can validate "basic" input data.

In the [next chapter](04-lists-and-dicts.md) we will take a detailed look on how to construct complex validators out of these basic
validators to validate lists and dictionaries, followed by [dataclasses](05-dataclasses.md) in a separate chapter.
