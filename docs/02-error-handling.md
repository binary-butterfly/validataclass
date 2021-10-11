# 2. Error Handling

Before we go into the details of the different validator classes and the validation of complex data structures, let's first examine
how to handle **validation errors**.


## What are validation errors?

When a validator decides that a given piece of input data is invalid, it raises a `ValidationError` exception.

More precisely, `ValidationError` is the **base class** of many different exception classes (which all can be found in the package
`validataclass.exceptions`). There are some common exceptions that are used by multiple validators (e.g. `RequiredValueError` and
`InvalidTypeError`), and more specific exceptions like `StringTooLongError`, `NumberRangeError` or `InvalidUrlError`.


### Error Codes

What all `ValidationError` classes have in common is that they have a property called `code`, which is a short string that describes
the type of error. All of those classes have a defined default code, e.g. `InvalidTypeError` has the code `"invalid_type"` by default,
but those default codes can be overwritten when an exception is created.

These codes are intended to be machine-readable and will rarely change between library versions (and if they do, it will be considered a
breaking change), so that for example frontends can use those strings to generate user-friendly and localized error messages.


### Extra Fields

Apart from the error **code**, a `ValidationError` may define so called **extra fields** that contain additional information on the error.
For example, `InvalidTypeError` has an extra field `expected_type` with a string describing what type the validator expected (in the case
that the validator allows more than one type, the field will be called `expected_types` instead, containing a list of strings), or an
`IntegerValidator` might raise a `NumberRangeError` with the extra fields `min_value` and `max_value` to tell the user which integer
values are allowed.


### Reasons

In some cases, a `ValidationError` may also have a `reason` property, which is a string that further explains the error. Contrary to
the error code, this is **not** a short and machine-readable string, but rather a full sentence. For example, the `UrlValidator` checks
multiple criteria to validate that a string is a valid URL, which all raise a `InvalidUrlError` with the same code `"invalid_url"`, but
with different reasons like `"Invalid URL format."` or `"URL scheme is not allowed."`. These strings are more for debugging purposes and
not suited very well for generating localized error messages. (This could be changed in a future version though, for example by adding a
`reason_code` property.)


### Nested errors

Some `ValidationError` subclasses even contain **nested errors**, that is, extra fields that contain one or more other `ValidationErrors`.
Examples for this are `ListItemsValidationError` and `DictFieldsValidationError`, which are raised by `ListValidator` and `DictValidator`
when there are validation errors in the individual items or fields of a list or dictionary.

More about this in the [chapter about lists and dictionaries](04-lists-and-dicts.md).


## Handling validation errors

To handle validation errors, we can use a regular `try ... except` construct around the `validate()` call.

In this example, we catch `ValidationError` exceptions and simply print them to standard output.

```pycon
>>> from validataclass.exceptions import ValidationError
>>> from validataclass.validators import StringValidator

>>> # Create your validator
>>> validator = StringValidator(min_length=1, max_length=10)

>>> # Get your input data (e.g. by parsing JSON data from HTTP requests)
>>> input_data = 'example string input that is way too long'

>>> # Validate data and handle validation errors
>>> try:
...     validated_input = validator.validate(input_data)
...     print('Input is valid:', validated_input)
... except ValidationError as error:
...     print('Validation error:', error)
...
Validation error: StringTooLongError(code='string_too_long', min_length=1, max_length=10)
```

This string representation is good for debugging, but not very suitable for end users.

Of course we can access the properties of the exception manually, e.g. `error.code` would be the code `"string_too_long"` and
`error.extra_data` would be a dictionary like `{'min_length': 1, 'max_length': 10}`. This might not always be very reliable though, since
some `ValidationError` classes define their own properties instead of using the `extra_data` dictionary.

The recommended way to handle validation errors is to use the method `error.to_dict()`. This will return a dictionary containing all
error data, including the field `code` and all extra fields:

```pycon
>>> try:
...     validated_input = validator.validate(input_data)
...     print('Input is valid:', validated_input)
... except ValidationError as error:
...     print('Validation error:', error.to_dict())
...
Validation error: {'code': 'string_too_long', 'min_length': 1, 'max_length': 10}
```

In `ValidationError` classes that support nested validation errors, the nested errors will be recursively converted to dictionaries, too.


### JSON API Responses

The `error.to_dict()` method is designed to be a convenient way to automatically generate error responses in a JSON based API.

Depending on how your application's error handling works in general, you could for example use the output from `error.to_dict()` directly
to generate a JSON response, or wrap the dictionary in your own application specific errors.

```pycon
>>> import json

>>> try:
...     validated_input = validator.validate(input_data)
...     response = do_something_with_your_input(validated_input)
... except ValidationError as error:
...     response = json.dumps(error.to_dict())
...
>>> response
'{"code": "string_too_long", "min_length": 1, "max_length": 10}'
```


## Example: JSON API

As a minimal but practical example for an actual application, let's imagine we're building a JSON API that takes a **list of integers**
(e.g. `[1, 2, 3]`), calculates the **sum** of those integers, and returns the result as JSON.

If the input is valid, the response might look like this: `{"result": 6}`.

If the input is not valid, an error response that wraps the validation error is returned: `{"error": {"code": "some_validation_error"}}`.

```python
import json

from validataclass.exceptions import ValidationError
from validataclass.validators import ListValidator, IntegerValidator

def handle_request(request_json: str) -> str:
    # Create a validator for a list of one or more integers
    validator = ListValidator(IntegerValidator(), min_length=1)

    try:
        # Parse JSON (error handling for malformed JSON is ignored here)
        input_data = json.loads(request_json)

        # Validate input
        integer_list = validator.validate(input_data)

        # Calculate sum and generate API response
        response = {
            'result': sum(integer_list),
        }

    except ValidationError as error:
        # Validation error! Generate error response
        response = {
            'error': error.to_dict(),
        }

    # Return API response as JSON
    return json.dumps(response)
```

Now, let's test this function:

```pycon
>>> # Valid input
>>> handle_request('[3]')
'{"result": 3}'
>>> handle_request('[42, 123, -4]')
'{"result": 161}'

>>> # Invalid input: List must have at least one item
>>> handle_request('[]')
'{"error": {"code": "list_invalid_length", "min_length": 1}}'

>>> # Invalid input: List items must be integers, not strings
>>> handle_request('["banana"]')
'{"error": {"code": "list_item_errors", "item_errors": {"0": {"code": "invalid_type", "expected_type": "int"}}}}'
```

And basically, that's it. :)


## Summary

Now we know how validation errors look like, how we can handle them, and even how to integrate the library in some small application.

In the [next chapter](03-basic-validators.md) we will go into the details of the different validator classes that are included in this
library, followed by the validation of more complex data structures like lists and dictionaries.
