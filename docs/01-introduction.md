# 1. Introduction

This library is a framework that provides an easy but powerful way to validate complex user input in Python applications.

While it was originally written to validate JSON data in REST APIs, you can use this library in pretty much any kind of application.
Most validators included in this library are intended to be used with basic data types like strings, integers, lists and dictionaries,
but the library is designed to be easily extendable, so feel free to build your own validators for whatever kind of data you have.

In this first chapter you will learn the basics of this library: What exactly is a "validator", what do they do, and how can we use them
to validate simple input data?

The following chapters will cover [error handling](02-error-handling.md), the different [types of validator classes](03-basic-validators.md)
included in this library, validation of [lists and dictionaries](04-lists-and-dicts.md), validation using [dataclasses](05-dataclasses.md),
and how to [build your own validators](06-build-your-own.md) or extend existing classes.


## What's a Validator?

Technically speaking, a **Validator** in validataclass is any class that implements the `validataclass.validators.Validator` base class.

Practically speaking, a **Validator** is a class with a `validate()` method, which takes an arbitrary piece of **input data** of any type,
performs various checks on that input data, and either raises a `ValidationError` exception if one of these checks fails, or returns a
defined, validated piece of **output data** if the input was valid.

Each validator class defines a specific set of checks, parameters and (sometimes) data transformations. For example, the first checks that
almost all validators do is that the input is not `None` and has a specific data type (e.g. `StringValidator` or `DateTimeValidator` both
expect the input to be strings, while `IntegerValidator` expects an integer, and `ListValidator` expects the input to be a list). After
those first checks, a validator might check other criteria, such as whether a string is formatted correctly (e.g. `DateTimeValidator`
would only accept strings that are formatted like `"2021-12-31T12:34:56+02:00"`).

Validator classes can also specify parameters and options for further configuration. For example, `StringValidator` has the optional
parameters `min_length` and `max_length` which specify a minimum and/or maximum length for input strings.

The output data of a validator (that is, the return value of the `validate()` method) also depends on the implementation of the validator.
Some validators return the input data unmodified (e.g. `IntegerValidator` checks that the input data is of type `int` and returns the same
integer value as output), while other validators perform data transformations or convert the input data to a specific class. For example,
the `DecimalValidator` converts an input string like `"1.234"` to a `decimal.decimal("1.234")` object (see [the "decimal" module of the
Python standard library](https://docs.python.org/3/library/decimal.html)).


## Examples

### First example: StringValidator

As a first example, let's create a simple `StringValidator`, which accepts input of type `str` and returns the input strings unmodified:

```pycon
>>> from validataclass.validators import StringValidator

>>> # Create the validator
>>> validator = StringValidator()

>>> # Validate some input data
>>> validator.validate('')
''
>>> validator.validate('banana')
'banana'
>>> validator.validate('this is a very long example sentence.')
'this is a very long example sentence.'
```

The `StringValidator` will raise an exception if the input data is not valid, for example because it has the wrong data type:

```pycon
>>> validator.validate(123)
# Raises exception: InvalidTypeError(code='invalid_type', expected_type='str')
```

These exceptions can later be used to generate detailed error responses to the user. We'll cover error handling in the next chapter.

Now, let's create another `StringValidator`, but this time with parameters to restrict the length of the input strings:

```pycon
>>> # Create a validator that accepts only strings with a length between 1 and 6 characters
>>> validator = StringValidator(min_length=1, max_length=6)

>>> # Validate the same input values from above
>>> validator.validate('')
# Raises exception: StringTooShortError(code='string_too_short', min_length=1, max_length=6)
>>> validator.validate('banana')
'banana'
>>> validator.validate('this is a very long example sentence.')
# Raises exception: StringTooLongError(code='string_too_long', min_length=1, max_length=6)
```

As you can see, there are different types of validation errors with specific error **codes** and (sometimes) additional information about
the error. We've already seen `InvalidTypeError` above, which has the **code** `"invalid_type"` and an **additional field** called
`expected_type` that specifies which type the validator would have accepted (here: `"str"`).

Now we have `StringTooShortError` and `StringTooLongError` with the codes `"string_too_short"` and `"string_too_long"`, and the additional
fields `min_length=1` and `max_length=6` which contain the specified minimum and maximum accepted string length. That way, we don't just
tell the user what's **wrong** with their data (it's too short or too long) but also give information on how the data **should** look like.


### Second example: DateTimeValidator

To demonstrate another validator that validates a bit more complex data, let's take a look at `DateTimeValidator`.

This validator accepts input strings with a date and time in a ISO 8601 compatible format and returns `datetime` objects from [the
"datetime" module of the Python standard library](https://docs.python.org/3/library/datetime.html#datetime.datetime). (Please note that
the validator does not support all variants of ISO 8601 datetime strings, just a specific subset of them. See the documentation of
`DateTimeValidator` for further information.)

```pycon
>>> from validataclass.validators import DateTimeValidator

>>> # Create the validator
>>> validator = DateTimeValidator()

>>> # Validate some input datetime strings
>>> validator.validate('2021-12-31T12:34:56+02:00')
datetime.datetime(2021, 12, 31, 12, 34, 56, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)))

>>> # This string has an invalid format
>>> validator.validate('31.12.2021 12:34')
# Raises exception: InvalidDateTimeError(code='invalid_datetime', datetime_format='<DATE>T<TIME>[<TIMEZONE>]')
```

There are lots of parameters for `DateTimeValidator` (e.g. whether a timezone is required in the input string, how to interpret datetimes
without a timezone, or to convert all input datetimes to a specific timezone) which will be covered later.

This validator is also a good example for **inheritence** of validator classes. `DateTimeValidator` is a subclass of `StringValidator`,
which in turn is a subclass of the base class `Validator`. The `StringValidator` part makes sure that the input is of type `str` (and also
that the string does not contain newlines or control characters). After that, the `DateTimeValidator` uses regular expressions and other
checks to make sure that the input string has a valid format, and converts the string to a `datetime` object.

Many validators make use of inheritence to reuse functionality of existing validators, and users of this library are highly encouraged to
create their own validators based on the built-in validator classes. We will cover this in a [later chapter](06-build-your-own.md).


### Third example: Dataclasses and nested validators

Before we continue with the next chapter, let's take a quick look at a (more or less) full example of what this library is really capable
of: Validating complex data with the help of dataclasses.

Imagine you're building a JSON based API that receives orders of fruits. Each **order** is a dictionary (parsed from a JSON object) that
has an integer `id`, a datetime `ordered_at` and a list of `items`. Each **item** is a dictionary with a string `name` and a `color`.
Also, the color is not an arbitrary string but is defined using an `Enum` class with a specific set of allowed string values (e.g. "red").

Instead of working with raw dictionaries, we will define two **dataclasses** `Order` and `Fruit` and associate each field of these
dataclasses with specific validators, and then use the `DataclassValidator` to parse raw input dictionaries to objects of our dataclasses.

If you feel overwhelmed by this example: Don't worry! We will cover validation of dictionaries and dataclasses in detail in a
[later chapter](05-dataclasses.md). For now, this is just to give a first impression of how the library can be used.

```python
from datetime import datetime
from enum import Enum
from typing import List

from validataclass.validators import *
from validataclass.helpers import validataclass


# Define a Enum class
class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'

# This defines a special variant of Python dataclasses
@validataclass
class Fruit:
    name: str = StringValidator()
    color: Color = EnumValidator(Color)

@validataclass
class Order:
    id: int = IntegerValidator()
    items: List[Fruit] = ListValidator(DataclassValidator(Fruit))
    ordered_at: datetime = DateTimeValidator()


# Create a validator for the Order dataclass
validator = DataclassValidator(Order)

# Example input dictionary
input_data = {
    'id': 42,
    'ordered_at': '2021-09-28T12:34:56+02:00',
    'items': [
        {'name': 'apple', 'color': 'green'},
        {'name': 'banana', 'color': 'yellow'},
    ],
}

# Validate input data, results in an object of the `Order` dataclass
validated_order = validator.validate(input_data)

# Print result
print(validated_order)
```

The result of this code will look something like this (formatted for better readability):

```
Order(
    id=42,
    items=[
        Fruit(name='apple', color=<Color.GREEN: 'green'>),
        Fruit(name='banana', color=<Color.YELLOW: 'yellow'>)
    ],
    ordered_at=datetime.datetime(2021, 9, 28, 12, 34, 56, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)))
)
```

What we see here is a `DataclassValidator` that accepts dictionaries, validates the fields of the input dictionary with validators that
are specified in the `Order` dataclass (using the special `@validator_dataclass` decorator), and creates `Order` objects from the input
data.

The fields `id` and `ordered_at` of the `Order` dataclass are simple values that are validated using an `IntegerValidator` and a
`DateTimeValidator`. This isn't different from the basic examples that we've seen earlier.

What's more interesting is the `items` field which is validated by a `ListValidator`. This validator first checks that the input is a
**list** of values, and then uses another `DataclassValidator` to validate every **item** of the list as a `Fruit` object. This in turn
uses a `StringValidator` and an `EnumValidator` and then creates `Fruit` objects. The end result is an `Order` object that contains a
**list** of `Fruit` objects.

In short: Validators can be **nested** to validate objects of any complexity. This can be combined with dataclasses to turn raw input
dictionaries into well-defined objects that are easy to work with.


## Summary

We have seen the basics of what validators are, what they do and how we can use them.

Continue to the [next chapter](02-error-handling.md), where we will learn more about **validation errors** and how to handle them.
