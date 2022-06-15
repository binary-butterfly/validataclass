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
  - `BigIntegerValidator`: Validates integers (variation of `IntegerValidator`)
  - `FloatValidator`: Validates floats (as `float`, not as `str`)
  - `DecimalValidator`: Validates decimal **strings** (e.g. `"1.23"`) to `decimal.decimal` objects
  - `FloatToDecimalValidator`: Validates floats (e.g. `1.23`) to `decimal.decimal` objects
  - `NumericValidator`: Validates integers, floats **and** decimal strings to `decimal.Decimal` objects

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

- Special validators:
  - `Noneable`: Wraps another validator but allows the input to be `None`
  - `NoneToUnsetValue`: Like `Noneable`, but converts `None` to `UnsetValue`
  - `AnythingValidator`: Accepts any input without validation (optionally with type restrictions)
  - `RejectValidator`: Rejects any input with a validation error (except for `None` if allowed)


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

The regex can be specified either as a precompiled pattern (see `re.compile()`) or as a string which will be compiled by
the class. Regex flags (e.g. `re.IGNORECASE` for case-insensitive matching) can only be set by precompiling a pattern
with those flags.

The input string will then be matched against the regex using `re.fullmatch()`, which means that the **full** string
must match the regex.

For further information on regular expressions, see: https://docs.python.org/3/library/re.html

This validator is based on the `StringValidator` (see above) and accepts all of its parameters, so you can use
`min_length`, `multiline`, etc. just like with the `StringValidator` (the same default values are applied here).

If the input string does not match the regex, a `RegexMatchError` validation error with the default error code
'invalid_string_format' is raised. To get more explicit error messages, you can specify a custom validation error
using the parameters `custom_error_class` (which must be a subclass of `ValidationError`) and/or `custom_error_code`
(which is a string that overrides the default error code).

By default, valid input strings are returned unmodified. Alternatively, you can specify an output template with the
`output_template` parameter which will then be expanded to generate the output string using
[`re.Match.expand`](https://docs.python.org/3/library/re.html#re.Match.expand), i.e. backreferences to regex groups
will be replaced with the groups' contents.

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

# Output templates: This validator accepts hexadecimal numbers in different formats (with "0x" prefix, with "0h" prefix
# or without any prefix), and uses an output template to always output the number in a fixed format (with "0x" prefix)
validator = RegexValidator(re.compile(r'(?:0[xh])?([0-9a-f]+)', re.IGNORECASE), r'0x\1')
validator.validate("123abc")    # will return "0x123abc"
validator.validate("0x123abc")  # will return "0x123abc"
validator.validate("0h123abc")  # will return "0x123abc"
validator.validate("0x")        # will raise RegexMatchError

# Same example, but setting a custom error code
validator = RegexValidator(re.compile(r'[0-9a-f]+'), custom_error_code='invalid_hex_number')
validator.validate("banana")  # will raise RegexMatchError, but with code='invalid_hex_number'

# Define a custom exception class instead of just setting a custom error code
from validataclass.exceptions import ValidationError

class InvalidHexNumberError(ValidationError):
    code = 'invalid_hex_number'

validator = RegexValidator(re.compile(r'[0-9a-f]+'), custom_error_class=InvalidHexNumberError)
validator.validate("banana")  # will raise a InvalidHexNumberError with its defined error code
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

Please note that this validator is a bit opinionated and simplified in that it does **not** allow every valid URL. It's
intended to be used primarily for HTTP URLs and thus only allows URLs with authority component (the `//host` part after
the colon).

By default the validator allows only the URI schemes "http" and "https", requires hostnames to have a top level domain
(e.g. "example.com" but not just "example"), allows IP addresses as host, and does not allow userinfo components in the URL.

The parameters `allowed_schemes`, `require_tld`, `allow_ip` and `allow_userinfo` can be used to change these defaults.
Please refer to the [documentation in the code](../src/validataclass/validators/url_validator.py) for details.

The maximum string length defaults to 2000 characters, but can be changed using the `max_length` parameter.

To allow empty strings as input, you can set the `allow_empty` parameter to `True` (defaults to `False`).

**Examples:**

```python
from validataclass.validators import UrlValidator

# Default options: Only allows "http(s)" as scheme, requires a TLD, allows IP, does not allow userinfo
validator = UrlValidator()
validator.validate("https://example.com")                        # returns string unmodified
validator.validate("http://123.45.67.89/foo")                    # returns string unmodified
validator.validate("http://example.com:8080/foo?bar=baz#bloop")  # returns string unmodified
validator.validate("")                   # will raise StringTooShortError
validator.validate("banana")             # will raise InvalidUrlError(reason='Invalid URL format.')
validator.validate("ftp://example.com")  # will raise InvalidUrlError(reason='URL scheme is not allowed.')
validator.validate("http://localhost")   # will raise InvalidUrlError(reason='Invalid host in URL.')

# Allow empty strings
validator = UrlValidator(allow_empty=True)
validator.validate("https://example.com")  # returns string unmodified ("https://example.com")
validator.validate("")                     # returns empty string unmodified ("")

# Set allowed schemes to "ftp" and "sftp" and allow userinfo components
validator = UrlValidator(allowed_schemes=['ftp', 'sftp'], allow_userinfo=True)
validator.validate("ftp://example.com/foo/bar")                     # returns string unmodified
validator.validate("sftp://username:password@example.com/foo/bar")  # returns string unmodified
validator.validate("https://example.com")  # will raise InvalidUrlError(reason='URL scheme is not allowed.')
```


## Numeric types

The following validators parse different types of numbers, namely **integers**, **floats** and **decimals**.

In most cases it is recommended to use either `IntegerValidator` or `DecimalValidator`. Floats are error-prone due to
how binary floating point arithmetics work, while integers and decimals are always precise.


### IntegerValidator

The `IntegerValidator` accepts and returns integer values. By default, only actual integers (i.e. no strings) are
accepted, so for example the string `"123"` would result in an `InvalidTypeError`.

The optional parameter `allow_strings` can be set to `True` to allow both integers and numeric strings as input. The
validator will convert strings to integers in that case, so the input values `123` (integer) and `"123"` (string) will
both result in the integer output value `123`.

Use the parameters `min_value` and/or `max_value` to set a value range (smallest and biggest allowed integer).
By default, these parameters are set so that only 32 bit integers are allowed, i.e. only integers from -2147483648
(`-2^32`) to 2147483647 (`2^32 - 1`).

However, these are just default values. To allow integers outside the 32-bit range, simply set `min_value` and
`max_value` to `None`. See also the `BigIntegerValidator` below.

**Examples:**

```python
from validataclass.validators import IntegerValidator

# Default: Accepts any 32-bit integer
validator = IntegerValidator()
validator.validate(0)            # will return 0
validator.validate(123)          # will return 123
validator.validate(-123)         # will return -123
validator.validate("1")          # will raise InvalidTypeError (use allow_strings=True or a DecimalValidator)
validator.validate(2147483648)   # will raise NumberRangeError(min_value=-2147483648, max_value=2147483647)
validator.validate(-2147483649)  # will raise NumberRangeError(min_value=-2147483648, max_value=2147483647)

# No value limits: Accepts any integer known to Python
validator = IntegerValidator(min_value=None, max_value=None)
validator.validate(2147483648)        # will return 2147483648
validator.validate(-2147483649)       # will return -2147483649
validator.validate(9999999999999999)  # will return 9999999999999999

# min_value parameter: Only allow zero or positive numbers
validator = IntegerValidator(min_value=0)
validator.validate(0)     # will return 0
validator.validate(123)   # will return 123
validator.validate(-123)  # will raise NumberRangeError(min_value=0, max_value=2147483647)

# min_value and max_value: Only allow values 1 to 10
validator = IntegerValidator(min_value=1, max_value=10)
validator.validate(0)   # will raise NumberRangeError(min_value=1, max_value=10)
validator.validate(1)   # will return 1
validator.validate(10)  # will return 10
validator.validate(11)  # will raise NumberRangeError(min_value=1, max_value=10)

# max_value only: Allow all values smaller than or equal to 10
validator = IntegerValidator(max_value=10)
validator.validate(1)      # will return 1
validator.validate(10)     # will return 10
validator.validate(11)     # will raise NumberRangeError(min_value=-2147483648, max_value=10)
# NOTE: This also allows any negative number (because no min_value is specified):
validator.validate(-1234)  # valid! will return -1234

# allow_strings parameter: Accept integers also as strings
validator = IntegerValidator(allow_strings=True)
validator.validate(42)      # will return 42
validator.validate("42")    # will return 42
validator.validate("-123")  # will return -123
validator.validate("foo")   # will raise InvalidIntegerError
```


### BigIntegerValidator

The `BigIntegerValidator` is a variation of the `IntegerValidator` with other default parameters.

It's exactly the same validator, just without the default values for `min_value` and `max_value` set by the regular
`IntegerValidator`, thus allowing arbitrarily big integers by default.

Basically, `BigIntegerValidator()` is a shorthand for `IntegerValidator(min_value=None, max_value=None)`.

You can still set `min_value` and/or `max_value` with this validator, e.g. to restrict input to positive integers.
If you need to set both parameters, you should use the regular `IntegerValidator` instead, since there is no point in
using the `BigIntegerValidator` then.

Like the IntegerValidator, it also supports the parameter `allow_strings` to allow strings as input.

**Examples:**

```python
from validataclass.validators import BigIntegerValidator

# Default: Accepts any integer
validator = BigIntegerValidator()
validator.validate(0)                # will return 0
validator.validate(123)              # will return 123
validator.validate(-123)             # will return -123
validator.validate(99999999999999)   # will return 99999999999999
validator.validate(-99999999999999)  # will return -99999999999999
validator.validate("1")              # will raise InvalidTypeError

# min_value parameter: Only allow zero or positive numbers
validator = BigIntegerValidator(min_value=0)
validator.validate(0)               # will return 0
validator.validate(123)             # will return 123
validator.validate(99999999999999)  # will return 99999999999999
validator.validate(-123)            # will raise NumberRangeError(min_value=0, max_value=2147483647)

# allow_strings parameter: Accept integers also as strings
validator = BigIntegerValidator(allow_strings=True)
validator.validate(42)                 # will return 42
validator.validate("99999999999999")   # will return 99999999999999
validator.validate("-99999999999999")  # will return -99999999999999
validator.validate("foo")              # will raise InvalidIntegerError
```


### FloatValidator

The `FloatValidator` accepts and returns float values. By default, only actual floats (i.e. no integers or strings) are
accepted, so for example the integer `1` and the string `"1.0"` would both result in an `InvalidTypeError`.

The optional parameter `allow_integers` can be set to `True` to allow integers as input which will then be converted to
floats, so the input values `1` (integer) and `1.0` (float) will both result in the float output value `1.0`.

If you want to validate decimal numbers in string format (e.g. `"1.234"`), see the `DecimalValidator` instead. (Using
`Decimal` instead of floats is generally recommended anyway in most cases (especially when working with money values!),
so if you're designing an API, please consider using decimal strings and Python's `Decimal` class.)

The `FloatValidator` also only allows finite values (i.e. neither `Infinity` nor `NaN` are accepted).

Optionally you can specify a range of valid values using `min_value` and `max_value`.

**Examples:**

```python
from validataclass.validators import FloatValidator

# Default options: Accepts any finite float value
validator = FloatValidator()
validator.validate(1.234)   # will return 1.234 (as float)
validator.validate(-0.001)  # will return -0.001
validator.validate(1.0)     # will return 1.0
validator.validate(1)       # will raise InvalidTypeError (use allow_integers=True or an IntegerValidator)
validator.validate("1.23")  # will raise InvalidTypeError (use DecimalValidator or FloatToDecimalValidator instead)

# allow_integers parameter: Accept integers and convert them to floats
validator = FloatValidator(allow_integers=True)
validator.validate(1.234)   # will return 1.234
validator.validate(42.0)    # will return 42.0
validator.validate(42)      # will return 42.0 (float, not integer!)
validator.validate("1.23")  # will still raise InvalidTypeError

# Value range: Only allow values from -1.0 to +1.0
validator = FloatValidator(min_value=-1.0, max_value=1.0)
validator.validate(0.123)   # will return 0.123
validator.validate(-1.0)    # will return -1.0
validator.validate(1.234)   # will raise NumberRangeError(min_value=-1.0, max_value=1.0)
validator.validate(-1.234)  # will raise NumberRangeError(min_value=-1.0, max_value=1.0)
```


### DecimalValidator

The `DecimalValidator` accepts decimal numbers **as strings** (e.g. `"1.234"`) and **converts** them to
`decimal.Decimal` objects (see [Python standard library](https://docs.python.org/3/library/decimal.html)).

Only allows finite numbers in regular decimal notation (e.g. `"1.234"`, `"-42"`, `".00"`, ...), but no other values that
are accepted by `decimal.Decimal` (e.g. no `Infinity` or `NaN` and no scientific notation).

Optionally a number range (minimum/maximum value either as `Decimal`, integer or decimal string), minimum/maximum number
of decimal places and a fixed number of decimal places in the output value can be specified.

A fixed number of output places will result in rounding according to the current decimal context (see `decimal.getcontext()`),
by default this means that `"1.49"` will be rounded to `1` and `"1.50"` to `2`.

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

# Value range: Can be either a Decimal object, decimal string or integer (but no float)
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

The `FloatToDecimalValidator` accepts **float** values (like the `FloatValidator`) and **converts** them to `Decimal`
objects (like the `DecimalValidator`). Internally it is based on the `DecimalValidator`.

By default, this validator only accepts floats as input. Optionally it can also accept integers by setting the parameter
`allow_integers=True`, e.g. the integer `42` will then result in a `Decimal('42')`, while the float `42.0` results in a
`Decimal('42.0')`. You can also set the parameter `allow_strings=True` to allow decimal strings, which will be parsed
by the underlying `DecimalValidator` (e.g. `"1.23"` will result in a `Decimal('1.23')`).

If you want to accept all three numeric input types (integers, floats and decimal strings), you can simply combine
`allow_integers=True` and `allow_strings=True`. As a shortcut for this, you can also use the `NumericValidator`, which
basically is just a `FloatToDecimalValidator` with those two options always enabled.

Like the `DecimalValidator` it supports the optional parameters `min_value` and `max_value` (specified as `Decimal`,
decimal strings, floats or integers), as well as `output_places`. However, it **does not** support the `min_places` and
max_places` parameters (those are technically not possible with floats)!

**Note:** Due to the way that floats work, the resulting decimals can have inaccuracies! It is recommended to use
`DecimalValidator` with decimal strings instead of floats as input whenever possible. This validator mainly exists for
cases where you need to accept floats as input.

**Examples:**

```python
from validataclass.validators import FloatToDecimalValidator

# Default options: Accepts any finite float value
validator = FloatToDecimalValidator()
validator.validate(1.234)   # will return Decimal('1.234')
validator.validate(1)       # will raise InvalidTypeError (use allow_integers=True or a IntegerValidator)
validator.validate("1.23")  # will raise InvalidTypeError (use allow_strings=True or an DecimalValidator)

# allow_integers parameter: Accept both floats and integers as input
validator = FloatToDecimalValidator(allow_integers=True)
validator.validate(42.0)    # will return Decimal('42.0')
validator.validate(42)      # will return Decimal('42')
validator.validate("1.23")  # will still raise InvalidTypeError

# allow_strings parameter: Accept both floats and strings as input
validator = FloatToDecimalValidator(allow_strings=True)
validator.validate(42.0)    # will return Decimal('42.0')
validator.validate("1.23")  # will return Decimal('1.23')
validator.validate(42)      # will still raise InvalidTypeError

# Number range and output places: Allow values from 0 to 1, always output with 3 decimal places
validator = FloatToDecimalValidator(min_value=0, max_value=1, output_places=3)
validator.validate(0.0)     # will return Decimal('0.000')
validator.validate(0.1234)  # will return Decimal('0.123')
validator.validate(0.1235)  # will return Decimal('0.124')
validator.validate(1.0)     # will return Decimal('1.000')
```


### NumericValidator

The `NumericValidator` accepts numeric values as integers, floats **and** decimal strings and converts all of them to
`decimal.Decimal` objects.

This validator is a special version of the `FloatToDecimalValidator` with the options `allow_integers` and `allow_strings`
always enabled, and is intended as a shortcut.

Like the `FloatToDecimalValidator`, the `NumericValidator` supports the optional parameters `min_value` and `max_value`
to specify the allowed value range, as well as `output_places` to set a fixed number of decimal places in the output
value.

**Examples:**

```python
from validataclass.validators import NumericValidator

# Accept any numeric value (integers, floats and decimal strings)
# This validator is equivalent to: FloatToDecimalValidator(allow_integers=True, allow_strings=True)
validator = NumericValidator()
validator.validate(123)      # will return Decimal('123')
validator.validate(1.234)    # will return Decimal('1.234')
validator.validate("1.234")  # will return Decimal('1.234')

# Number range and output places: Allow values from 0 to 00, always output with 2 decimal places
validator = NumericValidator(min_value=0, max_value=10, output_places=2)
validator.validate(0)        # will return Decimal('0.00')
validator.validate(0.0)      # will return Decimal('0.00')
validator.validate("0.000")  # will return Decimal('0.00')
validator.validate("1.234")  # will return Decimal('1.23')
validator.validate("1.235")  # will return Decimal('1.24')
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
from [`validataclass.helpers`](../src/validataclass/helpers/datetime_range.py) for further information.

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


## Special validators

There are a handful of validators that don't fit into the other categories and have special purposes.

These special validators most of the time don't validate that much on their own. For example, the `AnythingValidator`
and `RejectValidator` are special validators that accept/reject any input (with only a few configurable exceptions).

Some special validators are wrappers around other validators, for example the `Noneable` wrapper that allows `None` as
input value and passes all other values to the wrapped validator, or the `MultiTypeValidator` _(to be implemented!)_
that uses one of multiple wrapped validators depending on the type of input data.


### Noneable

The `Noneable` validator wraps another validator and additionally allows `None` as an input value.

Most validators do not allow `None` as input and raise an `RequiredValueError` instead. To allow the value to be `None`,
the `Noneable` wrapper can be used.

It first checks if the input value is `None`, in which case it simply returns `None`. In all other cases the input will
be passed to the wrapped validator as if it was used without `Noneable`.

Optionally a custom default value can be specified with the `default` parameter. If set, the `Noneable` validator
returns this default value instead of `None` when the input value is `None`.

Additionally, if the wrapped validator raises an `InvalidTypeError`, the wrapper will add `"none"` to the `expected_types`
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


### NoneToUnsetValue

The `NoneToUnsetValue` validator is a variation of the `Noneable` validator. It is equivalent to
`Noneable(validator, default=UnsetValue)`.

In other words, if the input value is `None`, this validator returns the special value `UnsetValue`. In all other cases,
the input is validated using the wrapped validator.

**Note:** The meaning of `UnsetValue` is explained later in the chapter about [dataclasses](05-dataclasses.md).

**Examples:**

```python
from validataclass.validators import NoneToUnsetValue, StringValidator

# Accepts all strings allowed by the StringValidator, and None, which is converted to UnsetValue
validator = NoneToUnsetValue(StringValidator())
validator.validate('banana')  # will return 'banana'
validator.validate('')        # will return '' (empty string)
validator.validate(None)      # will return UnsetValue
```


### AnythingValidator

The `AnythingValidator` is a special validator that accepts any input without further validation.

This validator can be used in places where it's not possible or necessary to validate the input but where the input
should still be preserved (e.g. as a field in a dataclass), or where the unvalidated data should be saved and properly
validated at a later point.

By default this validator accepts literally anything, including `None`. There are two optional parameters which can be
used to restrict the validator to some extend: `allow_none` and `allowed_types`.

To reject `None` as input, but accept anything else, you can set `allow_none=False`.

To only allow a certain set of input data types, you can set `allowed_types` to a list or set (or any iterable) of
types. The validator will do a type check on the input data then and reject any types that are not part of
`allowed_types`. Keep in mind that no further validation will be performed on the data.

Setting `allowed_types` will also cause the validator to reject `None` unless it is part of the allowed types. For
example, if you set `allowed_types=[str]`, only strings will be accepted. If you additionally want to allow `None`,
you can set `allow_none=True`. Alternatively you can also specify `type(None)` or `None` in the allowed types list.

The validation errors raised by this validator are `RequiredValueError` (only if `allow_none=False` or `allowed_types`
is used) and `InvalidTypeError` (only if `allowed_types` is used).

**Examples:**

```python
from validataclass.validators import AnythingValidator

# Accepts any input and returns it unmodified (including None)
validator = AnythingValidator()
validator.validate(None)  # returns None
validator.validate('')    # returns '' (empty string)
validator.validate(42)    # returns 42

# Accepts any input *except* for None
validator = AnythingValidator(allow_none=False)
validator.validate(None)  # raises RequiredValueError
validator.validate('')    # returns '' (empty string)
validator.validate(42)    # returns 42

# Accepts only integers and floats, which are returned unmodified (None is not allowed)
validator = AnythingValidator(allowed_types=[int, float])
validator.validate(None)  # raises RequiredValueError
validator.validate('')    # raises InvalidTypeError (with expected_types=['float', 'int'])
validator.validate(42)    # returns 42
validator.validate(1.23)  # returns 1.23

# Like above, accepts only integers and floats, but also allows None
# The following definitions are equivalent:
validator = AnythingValidator(allowed_types=[int, float], allow_none=True)
#         = AnythingValidator(allowed_types=[int, float, type(None)])
#         = AnythingValidator(allowed_types=[int, float, None])
validator.validate(None)  # returns None
validator.validate('')    # raises InvalidTypeError (with expected_types=['float', 'int', 'none'])
validator.validate(42)    # returns 42

# Accepts only dictionaries (which are returned completely unvalidated!)
validator = AnythingValidator(allowed_types=dict)
validator.validate(None)      # raises RequiredValueError
validator.validate('')        # raises InvalidTypeError (with expected_type='dict')
validator.validate({})        # returns {} (empty dictionary)
validator.validate({13: 12})  # returns {13: 12}
```


### RejectValidator

The `RejectValidator` is a special validator rejects any input with a validation error.

This validator can be used for example in dataclasses to define a field that may never be set, or to override an
existing field in a subclassed dataclass that may not be set in this subclass. Keep in mind that in a dataclass
you still need to define a default value for this field, e.g. with `DefaultUnset` or `Default(None)` (as explained
later), otherwise you have a dataclass with a field that is required but can never be valid.

By default, the validator literally rejects anything. In some cases you may want to allow `None` as the only valid
input value. This can be done by setting the parameter `allow_none=True`. In that case, the validator returns `None`
if `None` is the input value, and rejects anything else.

An alternative to allow `None` is to wrap the validator inside a `Noneable` validator. This can be useful in some cases
as the `Noneable` wrapper allows to convert the input `None` into a different value (see examples).

The validator raises a `FieldNotAllowedError` by default. Optionally you can set a custom exception class using
the parameter `error_class` (must be a subclass of `ValidationError`). There are also the parameters `error_code`
to override the default error code with a custom one, and `error_reason` to specify a detailed error message for
the user.

**Examples:**

```python
from validataclass.validators import RejectValidator, Noneable

# Rejects *any* input with the default exception (including None)
validator = RejectValidator()
validator.validate(None)  # raises FieldNotAllowedError
validator.validate(42)    # raises FieldNotAllowedError
validator.validate('')    # raises FieldNotAllowedError

# Accepts only None and rejects anything else
validator = RejectValidator(allow_none=True)
validator.validate(None)  # returns None
validator.validate(42)    # raises FieldNotAllowedError
validator.validate('')    # raises FieldNotAllowedError

# Use the Noneable wrapper to convert None into a different value, rejects anything else
validator = Noneable(RejectValidator(), default='')
validator.validate(None)  # returns '' (empty string)
validator.validate(42)    # raises FieldNotAllowedError
validator.validate('')    # raises FieldNotAllowedError

# NOTE: Even if None is converted to an empty string in this example, the empty string itself is
# not accepted as input by this validator. If you need a validator that does accept the empty
# string (and rejects anything else), consider using a StringValidator with max_length=0.

# Set a custom error code (but still raise FieldNotAllowedError exceptions)
validator = RejectValidator(error_code='custom_error_code')
validator.validate('foo')  # raises FieldNotAllowedError with custom code='custom_error_code'

# Set a reason text for a more detailed error message
validator = RejectValidator(error_reason='This field cannot be changed.')
validator.validate('foo')  # raises FieldNotAllowedError with reason='This field cannot be changed.'

# Define a custom exception class instead of just setting a custom error code
from validataclass.exceptions import ValidationError

class CustomValidationError(ValidationError):
    code = 'custom_error_code'

validator = RejectValidator(error_class=CustomValidationError)
validator.validate('foo')  # raises CustomValidationError (with its default code)

# Use the custom exception class but with a custom reason
validator = RejectValidator(error_class=CustomValidationError, error_reason='This field cannot be changed.')
validator.validate('foo')  # raises CustomValidationError with reason='This field cannot be changed.'
```


## Summary

We have seen a lot of different types of validators now and can validate "basic" input data.

In the [next chapter](04-lists-and-dicts.md) we will take a detailed look on how to construct complex validators out of these basic
validators to validate lists and dictionaries, followed by [dataclasses](05-dataclasses.md) in a separate chapter.
