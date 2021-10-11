# 4. Lists and Dictionaries

Now that we know how to validate different types of single value input data, let's learn how to validate **lists** and **dictionaries**,
which may even be nested (dictionaries in dictionaries, or dictionaries as list items, etc.).

In the [next chapter](05-dataclasses.md), we will then take a look at Python's **dataclasses** and how we can leverage them to neatly
integrate **data model** and **data validation** in a compact, declarative way.


## Lists

Let's begin with lists, because they are the most simple of these datastructures.

Lists can be validated using the `ListValidator` and a specified **item validator**. The item validator can be any kind of validator,
even another `ListValidator` (if you need to validate nested lists). For example, you could use an `IntegerValidator` as item validator
to validate a list of integers.

When validating input data, the `ListValidator` first ensures that the input data is actually a list (i.e. has the type `list`). Then
it iterates over the list and validates **every item** using the item validator. Only if **all** list items are valid, the `ListValidator`
will output a new list containing the **output values** of the item validator for each item.

If **at least one** list item fails validation, the `ListValidator` will raise a `ListItemsValidationError`. This error is special from
most other validation errors in that it contains **nested** validation errors: The validation errors that the item validator raised are
collected in a dictionary as "item errors". The keys of this dictionary are the indices of the invalid items (as integers, beginning
with 0). See the examples below.

By default the `ListValidator` accepts lists of any length, including the empty list (`[]`). The optional parameters `min_length` and
`max_length` can be used to specify a minimum and/or maximum number of items though.

**Note:** A `ListValidator` always has exactly **one** item validator which will be used for **all** items, so you cannot simply specify
multiple item validators to allow a list with mixed types. Instead, you can use a validator that accepts multiple types by itself as the
item validator though. Currently there is no built-in way to do this easily (in a future version there is going to be a meta validator
for that, where you can specify multiple validators for different types of input data). If you need this though, you can
[build your own special validator](06-build-your-own.md) for this.

**Examples:**

```python
from validataclass.validators import ListValidator, DecimalValidator, IntegerValidator

# Validate a list of decimal strings (results in a list of Decimal objects)
validator = ListValidator(DecimalValidator())
validator.validate([])                         # will return [] (empty list)
validator.validate(['42', '1.234', '-0.001'])  # will return [Decimal('42'), Decimal('1.234'), Decimal('-0.001')]
validator.validate([42, '1.234', '-0.001'])    # will raise ListItemsValidationError (first list item is not a string)
validator.validate(42)                         # will raise InvalidTypeError(excepted_type='list')

# Validate a list of integers with a minimum of 1 item and a maximum of 3 items
validator = ListValidator(IntegerValidator(), min_length=1, max_length=3)
validator.validate([])                # will raise ListLengthError(min_length=1, max_length=3)
validator.validate([42])              # will return [42]
validator.validate([42, 13, 12])      # will return [42, 13, 12]
validator.validate([42, 13, 12, 11])  # will raise ListLengthError(min_length=1, max_length=3)

# Nested lists: Validate a *list of list of integers*
validator = ListValidator(ListValidator(IntegerValidator()))
validator.validate([[1, 2, 3], [42], [0, 0, 0]])  # will return [[1, 2, 3], [42], [0, 0, 0]]
```


### Validation errors in list items

As mentioned above, if one or more items fail validation, a **nested** `ListItemsValidationError` is raised, containing all validation
errors for the individual items. The `to_dict()` method of this exception will recursively use `to_dict()` to convert the nested errors
to dictionaries too, resulting in a nested dictionary.

**Example for nested validation errors:**

```python
from validataclass.exceptions import ValidationError
from validataclass.validators import ListValidator, DecimalValidator

# Create a validator for a list of decimals between 1 and 100
validator = ListValidator(DecimalValidator(min_value='1', max_value='100'))

# Construct an input list with multiple invalid items (for various reasons)
input_list = [
    42,        # 0: invalid (must be a string)
    '1.234',   # 1: valid
    'banana',  # 2: invalid (not a valid decimal string)
    '42',      # 3: valid
    '1234',    # 4: invalid (valid decimal, but outside the range 1-100)
]

# Try to validate the list and print the resulting ListItemsValidationError as a dictionary
try:
    validator.validate(input_list)
except ValidationError as error:
    print(error.to_dict())
```

**Output** (formatted for better readability):

```pycon
{
    'code': 'list_item_errors',
    'item_errors': {
        0: {'code': 'invalid_type', 'expected_type': 'str'},
        2: {'code': 'invalid_decimal'},
        4: {'code': 'number_range_error', 'min_value': '1', 'max_value': '100'}
    }
}
```


## Dictionaries

Dictionaries can be validated using the `DictValidator` and **one or more** specified **field validators**. A field validator can be any
kind of validator, including another `DictValidator` (nested dictionaries). Contrary to the `ListValidator` which uses the same item
validator for all items, you specify one field validator for each key the dictionary may have. Additionally (or alternatively) a
**default validator** can be specified that will be used to validate all fields that don't have a designated field validator.

The parameters to specify these validators are `field_validators` (which is a dictionary that maps field names to validators) and
`default_validator` (which is a validator object). You need to specify **at least one** of those parameters.

By default, all fields that are defined in `field_validators` will be **required fields** (i.e. the validation will fail if one of these
fields does not exist in the input dictionary). This can be overridden with the `required_fields` parameter, which is a list of the keys
that are required. To make all fields optional, simply set `required_fields=[]`.

As an alternative to `required_fields` there also is the parameter `optional_fields`. Setting this to a list of keys will implicitly
set `required_fields` to all fields defined in `field_validators` **except those** in `optional_fields`.

When validating input data, the `DictValidator` first ensures that the input data is actually a dictionary (i.e. has the type `dict`)
and that all keys of the dictionary are strings (see note below). It further checks if any **required field** is missing in the input
dictionary. Then it iterates over all fields in the dictionary. If a field validator is defined for a field, the field **value** will
be validated using this field validator. Otherwise, the **default validator** will be used. If no default validator is defined, the field
will be **silently discarded** (i.e. it does not result in a validation error). The output of the `DictValidator` will be new dictionary
containing the same fields of the input dictionary (except those that were discarded) with the values being the output of the field
(or default) validators.

If **any** dictionary field fails validation or a required field is missing, the `DictValidator` will raise a `DictFieldsValidationError`.
Like the `ListItemsValidationError`, this error contains **nested** validation errors. All validation errors raised by the field
validators are collected in a dictionary as "field errors", with the keys being the field names. Missing required fields will result in
a `DictRequiredFieldError` in the same field errors dictionary.

**Note:** As of now, only **strings** are allowed as dictionary keys. When working with JSON data, this should be sufficient, since
JSON only supports string keys in dictionaries anyway. Keys can still be numeric strings though, e.g. `{"1": "foo"}` would be a valid
dictionary. If you do need dictionaries with non-string keys, feel free to open an issue for this, or [extend the
DictValidator](06-build-your-own.md) for your usecase.

**Examples:**

```python
from validataclass.validators import DictValidator, IntegerValidator, StringValidator, DecimalValidator

# Validate a dictionary with three fields: "id" (integer), "name" (string), "price" (non-negative Decimal).
# All three fields are required, since neither required_fields nor optional_fields was set explicitly.
validator = DictValidator(field_validators={
    'id': IntegerValidator(),
    'name': StringValidator(),
    'price': DecimalValidator(min_value='0'),
})

validator.validate({'id': 3, 'name': 'Foo', 'price': '1.23'})  # returns {'id': 3, 'name': 'Example', 'price': Decimal('1.23')}
validator.validate({'id': 3, 'name': 'Foo'})                   # raises DictFieldsValidationError (with DictRequiredFieldError for 'price')
validator.validate({'id': 3, 'name': 'Foo', 'price': '-1.23'}) # raises DictFieldsValidationError (with NumberRangeError for 'price')
validator.validate({'id': 3, 'name': 1, 'price': '1.23'})      # raises DictFieldsValidationError (with InvalidTypeError for 'name')

# Also, since no default_validator is defined, all additional fields (that are not defined in field_validators) will be silently
# discarded. So this example results in the same output dictionary as the first input example above:
validator.validate({'id': 3, 'name': 'Foo', 'price': '1.23', 'foo': 'banana', 'bar': 42})

# Same field validators as above, but make the "price" field optional
validator = DictValidator(
    field_validators={
        'id': IntegerValidator(),
        'name': StringValidator(),
        'price': DecimalValidator(min_value='0'),
    },
    optional_fields=['price']  # Equivalent to: required_fields=['id', 'name']
)

validator.validate({'id': 3, 'name': 'Foo', 'price': '1.23'})  # returns {'id': 3, 'name': 'Example', 'price': Decimal('1.23')}
validator.validate({'id': 3, 'name': 'Foo'})                   # returns {'id': 3, 'name': 'Example'}
validator.validate({'id': 3})                                  # raises DictFieldsValidationError (with DictRequiredFieldError for 'name')

# Validate a dictionary without predefined field names using a default validator.
# Allows arbitrary strings as keys, with decimals as values.
validator = DictValidator(default_validator=DecimalValidator())
validator.validate({})                                   # returns {} (empty dictionary)
validator.validate({'banana': '1.23', 'apple': '0.42'})  # returns {'banana': Decimal('1.23'), 'apple': Decimal('0.42')}
validator.validate({'banana': '1.23', 'apple': 42})      # raises DictFieldsValidationError (with InvalidTypeError for 'apple')

# Even without field_validators, you can specify required fields
validator = DictValidator(default_validator=DecimalValidator(), required_fields=['banana'])
validator.validate({'banana': '1.23', 'apple': '0.42'})  # returns {'banana': Decimal('1.23'), 'apple': Decimal('0.42')}
validator.validate({'apple': '0.42'})                    # raises DictFieldsValidationError (with DictRequiredFieldError for 'banana')

# You can also combine field_validators and default_validator.
# This example allows arbitrary keys for decimal fields, but additionally requires an integer "id" field.
validator = DictValidator(
    field_validators={'id': IntegerValidator()},
    default_validator=DecimalValidator(),
)

validator.validate({'id': 3, 'foo': '1.2', 'bar': '0.5'})    # returns {'id': 3, 'foo': Decimal('1.2'), 'bar': Decimal('0.5')}
validator.validate({'foo': '1.2', 'bar': '0.5'})             # raises DictFieldsValidationError (with DictRequiredFieldError for 'id')
validator.validate({'id': '3', 'foo': '1.2', 'bar': '0.5'})  # raises DictFieldsValidationError (with InvalidTypeError for 'id')
```


### Validation errors in dictionary fields

Like with the `ListItemsValidationError`, the `to_dict()` method of the `DictFieldsValidationError` will recursively generate a nested
dictionary containing dictionaries for all field errors.

**Example for nested validation errors:**

```python
from validataclass.exceptions import ValidationError
from validataclass.validators import DictValidator, IntegerValidator, StringValidator, DecimalValidator

# Construct a validator with different types of fields
validator = DictValidator(field_validators={
    'id': IntegerValidator(),
    'name': StringValidator(),
    'price': DecimalValidator(min_value='0'),
})

# Construct an input dictionary with multiple invalid or missing items
input_dict = {
    'id': '42',          # Field "id": Invalid type (must be integer)
                         # Field "name": Required field is missing
    'price': '-1.23',    # Field "price": Valid decimal, but outside the valid number range (value less than 0)
    'banana': 'banana',  # No validator defined for field "banana" -> Field will be discarded, NOT an error!
}

# Try to validate the dictionary and print the resulting ListItemsValidationError as a dictionary
try:
    validator.validate(input_dict)
except ValidationError as error:
    print(error.to_dict())
```

**Output** (formatted for better readability):

```pycon
{
    'code': 'field_errors',
    'field_errors': {
        'name': {'code': 'required_field'},
        'id': {'code': 'invalid_type', 'expected_type': 'int'},
        'price': {'code': 'number_range_error', 'min_value': '0'}
    }
}
```


## Summary

We have now learned how to validate lists and dictionaries which can contain all sorts of data. This basically is enough to build
validators for most use cases (e.g. JSON APIs).

But dictionaries can be cumbersome to work with and are prone to error, especially when your application is growing and there are lots
of different types of input dictionaries.

This is where the key feature of this library comes into play: Validating dictionaries with **dataclasses**.

Continue with [the next chapter](05-dataclasses.md) to learn about dataclasses and how to use them for validation.
