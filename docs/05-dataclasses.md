# 5. Validation with Dataclasses

In this chapter we will finally learn about the key feature of this library: Validation of dictionaries using **dataclasses**.

But first, let's talk about what dataclasses are in the first place and why we would want to use them.


## Why dataclasses?

Now, we already can validate dictionaries using the `DictValidator`, which gives us a dictionary with validated fields. Those should
be safe to work with, right?

Yes, but also no.

Yes, we can be sure that the data inside our dictionaries is valid and safe to work with (as long as we used the correct validators),
which undoubtedly is better than working with raw, unvalidated dictionaries.

But from a code perspective, dictionaries don't have any inner structure by themselves, they're just key-value stores with arbitrary data.
This makes it difficult for type checkers or code linters (including IDEs like Pycharm) to analyse the code that's working with the
input data. For example, a type checker doesn't know that a specific field in this dictionary has been validated using a `DecimalValidator`
and therefore must be a `Decimal` object. Similarly, your IDE cannot warn you about the wrong key in `validated_dict['prize']` (which
should have been `'price'` instead), not to mention code autocompletion.

Dataclasses can solve these problems (and help you write much better code along the way): Instead of working with plain dictionaries,
you can define dataclasses and create objects with well-defined and type-annotated properties from your input data.

But what exactly is a dataclass anyway?


## What are dataclasses?

[Dataclasses](https://docs.python.org/3/library/dataclasses.html) are a special kind of user-defined classes which are defined using
the `@dataclass` decorator. This decorator auto-generates special methods like `__init__()` or `__repr__()` by looking at the **fields**
of the class, which mostly are just type-annotated class variables.

Technically, a dataclass in itself really isn't anything special at all, it is just a regular class with some auto-generated boilerplate
methods, which you normally would have written yourself. For example, imagine the following class:

```python
from decimal import Decimal

class OrderItem:
    id: int
    name: str
    price: Decimal
    amount: int = 1  # This variable is optional and has the default value 1

    def __init__(self, id: int, name: str, price: Decimal, amount: int = 1):
        self.id = id
        self.name = name
        self.price = price
        self.amount = amount

    def __repr__(self):
        return f'OrderItem(id={self.id}, name={self.name}, price={self.price}, amount={self.amount})'

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return (self.id, self.name, self.price, self.amount) == \
                   (other.id, other.name, other.price, other.amount)
        return NotImplemented

    # [... maybe even some more special methods ...]
```

The `@dataclass` decorator would automatically generate the special methods we see above. So, the following example basically is the
same class with the same `__init__()`, `__repr__()` and `__eq__()` methods, just with less code:

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class OrderItem:
    id: int
    name: str
    price: Decimal
    amount: int = 1  # This variable is optional and has the default value 1
```

To create objects from this dataclass, you only need to specify the dataclass fields as keyword arguments to the constructor:

```pycon
order_item = OrderItem(id=42, name='Banana', price=Decimal('1.23'))
print(order_item)       # prints: OrderItem(id=42, name='Banana', price=Decimal('1.23'), amount=1)
print(order_item.name)  # prints: Banana
```

There is a lot more that you can do with dataclasses, but this is beyond the scope of this documentation.


## How to use dataclasses?

Basically, we already know everything we need to combine dictionary validation with dataclasses.

Let's take the first `DictValidator` example from above (dictionary with `"id"`, `"name"` and `"price"`), define a dataclass for it,
and convert a validated dictionary to an object of this dataclass.

You may notice the dataclass very much looks like the dataclass example from above. Coincidence...? (For simplicity, we will ignore
the optional `"amount"` field for now, though.)

```python
from dataclasses import dataclass
from decimal import Decimal

from validataclass.validators import DictValidator, IntegerValidator, StringValidator, DecimalValidator

@dataclass
class OrderItem:
    id: int
    name: str
    price: Decimal

# Copy the DictValidator from above
validator = DictValidator(field_validators={
    'id': IntegerValidator(),
    'name': StringValidator(),
    'price': DecimalValidator(min_value='0'),
})

# Example input dictionary
input_dict = {
    'id': 42,
    'name': 'Banana',
    'price': '1.23',
}

# First, validate the input data as usual
validated_dict = validator.validate(input_dict)  # returns {'id': 42, 'name': 'Banana', 'price': Decimal('1.23')}

# Now, create an OrderItem object from the validated dictionary.
# Note: We need the **-operator here to unpack the dictionary to keyword arguments for the constructor.
order_item = OrderItem(**validated_dict)

# Now we can work with an OrderItem instead of a dictionary!
print(order_item)
print(f'User ordered a {order_item.name} for {order_item.price} money units.')
```

**Output:**

```text
OrderItem(id=42, name='Banana', price=Decimal('1.23'))
User ordered a Banana for 1.23 money units.
```

We now have successfully validated a dictionary using a `DictValidator` and converted it to an object of a dataclass.

Now, this is great and all, but this code isn't very elegant, especially when we start defining more and more dataclasses for different
types of input dictionaries.

For one thing, we need to define everything twice: Define the fields in the dataclass with type annotations, and define the same fields
with field validators in the `DictValidator`. For another thing, we need to manually convert the dictionary to a dataclass object after
validation, instead of having a validator that directly outputs the dataclass object. This might not look like a big deal in our
example, but imagine you have nested dictionaries and want to convert the inner dictionaries to dataclass objects too. With this
approach, this would be very tedious.

The last thing could be solved by subclassing the `DictValidator` to an `OrderItemValidator` and doing the dataclass conversion directly
inside the `validate()` method. You could also easily move the definition of the field validators into this subclass. But this wouldn't
solve the first (and arguably much bigger) problem.

But what if we could move the definition of the field validators **directly into the dataclass**?
Turns out, there is a very elegant way to do this!

_Let me tell you about the `DataclassValidator`._


## The DataclassValidator

The `DataclassValidator` basically is just a very specialized `DictValidator`. It validates dictionaries using **field validators**,
and then converts the validated dictionaries to objects of a specified **dataclass**.

But instead of specifying the field validators in the validator, you can now define the validators directly inside the dataclass.
The `DataclassValidator` will read these field validators from the dataclass and pass them to the underlying `DictValidator`. In the
same way it also determines which fields are required and which are optional.

The usage of the `DataclassValidator` then is pretty trivial, assuming we have already defined the dataclass:

```python
from validataclass.validators import DataclassValidator

validator = DataclassValidator(OrderItem)
validator.validate({'id': 42, 'name': 'Banana', 'price': '1.23'})  # returns OrderItem(id=42, name='Banana', price=Decimal('1.23'))
validator.validate({'id': 42, 'name': 'Banana', 'price': 3})       # raises DictFieldsValidationError (with InvalidTypeError for 'price')
```

Now the question is, how can we define field validators inside a dataclass so that the `DataclassValidator` can read them out?


## Defining field validators in a dataclass

For this, we first need to understand a little bit more how dataclasses (that is, the `@dataclass` decorator) work: Every class variable
with a type annotation (e.g. `some_var: int` or `some_var: int = 42`) is considered a "field" in a dataclass and is represented by
[an internal `Field` object](https://docs.python.org/3/library/dataclasses.html#dataclasses.Field). In most cases, these `Field` objects
are created implicitly by the `@dataclass` decorator, but you can also create a field explicitly using the
[`field()`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field) function, e.g. `some_var: int = field(default=42)`.

Now, the `field()` function has a few parameters (see Python documentation). One of these parameters is `metadata`, which can be set to
an arbitrary dictionary. It doesn't have any meaning for dataclasses on its own and is intended to be used _"as a third-party extension
mechanism"_, so we can use it for example to store a validator directly in the dataclass field.

The `DataclassValidator` then examines the `metadata` attribute of each dataclass field and looks for the `"validator"` key to find the
field's validator. (Additionally, the metadata key `"default"` can be used to set a default value for the field and thus make the
field optional, but we will go into detail about this later.)

So, using the `metadata` attribute, we could define the dataclass from our example like this:

```python
from dataclasses import dataclass, field
from decimal import Decimal

from validataclass.validators import IntegerValidator, StringValidator, DecimalValidator, DataclassValidator

@dataclass
class OrderItem:
    id: int = field(metadata={'validator': IntegerValidator()})
    name: str = field(metadata={'validator': StringValidator()})
    price: Decimal = field(metadata={'validator': DecimalValidator(min_value='0')})

# Use the dataclass in a DataclassValidator
validator = DataclassValidator(OrderItem)
```

This is much more compact than the `DictValidator` approach, but there is still room for improvement, as the metadata definitions are
quite repetitive and bulky. Luckily, there are two helper functions to simplify our dataclasses: The `validataclass_field()` function
and the even more powerful `@validataclass` decorator.


### Creating fields with `validataclass_field()`

The obvious solution for simplifying the field definitions is to write a wrapper for the dataclass `field()` function that defines the
metadata for us. This wrapper is `validataclass_field()`: It takes a validator (and optionally a default value) as argument and generates
the `field()` call for us. Additional keyword arguments can be specified, which will be passed to the `field()` function to keep it
(mostly) compatible to the original function.

Using this function, our dataclass looks like this now:

```python
from dataclasses import dataclass
from decimal import Decimal

from validataclass.helpers import validataclass_field
from validataclass.validators import IntegerValidator, StringValidator, DecimalValidator, DataclassValidator

@dataclass
class OrderItem:
    id: int = validataclass_field(IntegerValidator())
    name: str = validataclass_field(StringValidator())
    price: Decimal = validataclass_field(DecimalValidator(min_value='0'))

# Use the dataclass in a DataclassValidator
validator = DataclassValidator(OrderItem)
```

This is better than manually defining the metadata for every field, but we can go even a step further and drop the `validataclass_field()`
call altogether by using the `@validataclass` decorator.


### The `@validataclass` decorator

The `@validataclass` decorator is a wrapper around the regular `@dataclass` decorator.

It first "prepares" a class by creating **implicit fields** with `validataclass_field()` where necessary (similar to how `@dataclass`
creates implicit fields). Then it applies the regular `@dataclass` decorator to the class, which turns it into a dataclass as usual.

To prepare the fields, the `@validataclass` decorator looks at all type-annotated class variables and checks their value. If a field
has already been defined explicitly (either using `validataclass_field()` or using the regular `field()` function), nothing needs to be
done. If the value is a `Validator` object, a field is created using `validataclass_field()` with this validator. A special format using
tuples can also be used to specify a field default (explained later). In all other cases (including when a class variable has no value
set at all), the decorator will raise an exception.

Here is our dataclass example again, now using the `@validataclass` decorator:

```python
from decimal import Decimal

from validataclass.helpers import validataclass
from validataclass.validators import IntegerValidator, StringValidator, DecimalValidator, DataclassValidator

@validataclass
class OrderItem:
    id: int = IntegerValidator()
    name: str = StringValidator()
    price: Decimal = DecimalValidator(min_value='0')

# Use the dataclass in a DataclassValidator
validator = DataclassValidator(OrderItem)
```

**Note:** You may wonder why we introduced the `validataclass_field()` function at all, when we can just define dataclasses using the
`@validataclass` decorator instead. One reason is simply to help you understand how the `@validataclass` decorator works, because it
uses the `validataclass_field()` function internally itself. But there may also be cases where you need this function to define a field
explicitly, for example to specify [other `field()` parameters](https://docs.python.org/3/library/dataclasses.html#dataclasses.Field).

It is also worth noting that you can use the `@validataclass` decorator with optional keyword arguments, which will be passed to the
`@dataclass` decorator. For example, using `@validataclass(repr=False, order=True)` would result in `@dataclass(repr=False, order=True)`
being applied to the class.


## Defining field defaults

While dataclasses have built-in support for field default values, they unfortunately have a rather impractical restriction on the order
of fields: In a dataclass, all optional fields (i.e. fields with default values) must be defined **after** all of the required fields.
Defining a required field (i.e. a field without default value) after an optional field will result in an error:

```python
from dataclasses import dataclass

@dataclass
class ExampleDataclass:
    var1: int
    var2: str = 'some default value'
    var3: int  # This raises a TypeError because the field has no default value!
```

In this example, you would either have to move the `var3` field above `var2` or define a default for `var3`.

To circumvent this restriction, we opted to implement our own default value handling in the `DataclassValidator`. Like the field
validators, the field defaults are stored in the **metadata** of the field, namely under the key `"validator_default"`. From the point
of view of the dataclass, all fields will be "required" fields because no `default` attributes are set. The `DataclassValidator` will
fill the missing fields in the input dictionaries with the default values before attempting to create dataclass objects from them. 

Further, the `DataclassValidator` will see all fields as required **unless** they have a **default value**. To define an optional field
**without** a default value, use the `DefaultUnset` object (which is explained later).

Of course, both the `validataclass_field()` function and the `@validataclass` decorator support setting the metadata for default values.  


### Setting defaults with `validataclass_field()`

To set a default value with `validataclass_field()`, you simply specify the `default` parameter. This parameter can be set either to a
`Default` object (which we will explain in a moment) or directly to a value.

**Example:**

```python
from dataclasses import dataclass

from validataclass.helpers import validataclass_field, Default
from validataclass.validators import IntegerValidator

@dataclass
class ExampleDataclass:
    # The following fields are equivalent
    field_a: int = validataclass_field(IntegerValidator(), default=42)           # Specify default as direct value
    field_b: int = validataclass_field(IntegerValidator(), default=Default(42))  # Specify default using a Default object
```


### Setting defaults with `@validataclass`

To set a default value for a field using the `@validataclass` decorator, you have to define the field as a **tuple** consisting of the
validator and a `Default` object, e.g. `IntegerValidator(), Default(42)`.

Please note that in Python 3.7 for some reason these tuples require parentheses (see example). Unless you're writing code for Python 3.7,
it is recommended to omit the parentheses for a more consistent look, though.

**Example:**

```python
from validataclass.helpers import validataclass, Default
from validataclass.validators import IntegerValidator, StringValidator

@validataclass
class ExampleDataclass:
    example_field: int = IntegerValidator()
    optional_field: int = IntegerValidator(), Default(42)
    
    # Compatibility note: In Python 3.7 parentheses are required when using the tuple notation:
    optional_field2: int = (IntegerValidator(), Default(42))
```


### The `Default` classes

To specify default values for fields, the helper class `Default` can be used. There also are some subclasses of `Default` which will be
covered in a moment: `DefaultFactory`, `DefaultUnset` and `NoDefault`.


#### Default (base class)

Use the `Default` class if you want to specify a single, constant value as a field default. This class is basically just a wrapper that
encapsulates a "raw" value in an object and returns this value if needed. The value can be of any type (including `None` or some object).

For example, with `Default('')` the default would always be an empty string, `Default(42)` would set the default to the integer `42`,
and `Default(None)` would result in the default value being `None`.

The value will be deepcopied, which means that if you use lists, dictionaries or objects as default values, every validated object will
have a **copy** of the value. For example, with `Default([])` the default would always be a new empty list. Modifying the list of one
validated object would **not** result in a change of the list of other validated objects.


#### DefaultFactory

The `DefaultFactory` class uses **callables** to generate default values dynamically at validation time. Use this class if you need
dynamic default values.  You can use a `DefaultFactory` with any callable, e.g. with a function reference or a lambda function.

For example, specifying `DefaultFactory(datetime.now)` (with `from datetime import datetime`) would result in the default value always
being the datetime at which the input dictionary was validated. To use the current year as default, you could use a lambda function:
`DefaultFactory(lambda: datetime.now().year)`.

Contrary to `Default` the values will **not** be deepcopied. This also means that you can use a `DefaultFactory` as a workaround if you
actually want to use an object **reference** as a default value. For example, if you have a list `some_list = []` and use a
`DefaultFactory(lambda: some_list)` as default for a dataclass field, all objects validated using this dataclass with use **the same**
list as their default. Modifying the list of one validated object will modify the list for **all** objects.


#### DefaultUnset and the `UnsetValue` object

If you set a default value for a field in a dataclass, this field will **always** have a value: Either the value from the input dictionary
if the field exists, or the default value. If you don't set a default value, the field is **required**, meaning an input dictionary
without this field will fail validation.

Sometimes you want optional fields **without** default values though: If a string field uses `Default('')` for example, it will always
have a string value (either empty or not empty), and you cannot distinguish whether the field was missing in the input dictionary or
whether the field was literally an empty string.

One solution is to use `Default(None)` instead: If the field is `None`, you know that the field did not exist in the input dictionary.

This is sufficient in a lot of cases, but sometimes `None` is an allowed value for a field (e.g. when using the `Noneable` meta validator)
and you need to distinguish between "the field did not exist" and "the field was explicitly set to `None`".

For this case, we defined a special value called `UnsetValue`, which you can use similarly to `None`. These values are so called
[sentinel objects](https://python-patterns.guide/python/sentinel-object/): Their purpose is to represent a missing value. They also are
unique objects, which means you cannot copy them: Trying to create a new object using `UnsetValue()` or even using `deepcopy(UnsetValue)`
will always result in a reference to the **same** object. This ensures that you can check for this value using the identity operator `is`,
e.g. `if some_value is UnsetValue` (just like `is None` or `is True`).

So, to define an **optional field without default** you can simply specify `UnsetValue` as the default value, and then use `is UnsetValue`
in your code to distinguish it from other values like `None`.

For this you can use the `DefaultUnset` object, which is a shortcut for `Default(UnsetValue)`.

Remember to adjust the type hints in your dataclass though. For example: `some_var: Union[int, UnsetValueType]`.


#### NoDefault

Specifying the `NoDefault` object for a field default literally means that the field does not have any default value. This is equivalent
to **not specifying a default value at all**, meaning the field will be **required** and not optional.

You will probably never need to specify this value explicitly.


#### Examples for the various Default classes

The following code contains examples for all the various `Default` classes that we've seen above.

```python
from datetime import datetime
from typing import Optional, Union

from validataclass.helpers import validataclass, Default, DefaultUnset, DefaultFactory, UnsetValueType, NoDefault
from validataclass.validators import IntegerValidator, ListValidator, DateTimeValidator

@validataclass
class ExampleClass:
    # Simple defaults for integer fields
    field_a: int = IntegerValidator(), Default(42)                          # Default value is 42
    field_b: Optional[int] = IntegerValidator(), Default(None)              # Default value is None
    field_c: Union[int, UnsetValueType] = IntegerValidator(), DefaultUnset  # Default value is UnsetValue
    
    # Defaults for lists
    field_d: list = ListValidator(IntegerValidator()), Default([])  # Default value is an empty list
    
    # DefaultFactories for datetime fields
    field_e: datetime = DateTimeValidator(), DefaultFactory(datetime.now)           # Default value will be datetime of validation
    field_f: int = IntegerValidator(), DefaultFactory(lambda: datetime.now().year)  # Default value will be YEAR of validation (as int)
    
    # No default: The following two fields are exactly the same (both are required)
    field_g: int = IntegerValidator()
    field_h: int = IntegerValidator(), NoDefault
```


### Note about `None` values and `Noneable`

One more important thing to understand about optional fields is what "optional" exactly means.

When a field is optional, this means that the field is allowed to be **omitted completely** in the input dictionary. However, this
does **not** automatically mean that the input value is allowed to have the value `None`. A field with a default value would still raise
a `RequiredValueError` if the input value is `None`. This is, unless a field validator that explicitly allows `None` as value is used.

For example, imagine a dataclass with only one field: `some_var: Optional[int] = IntegerValidator(), Default(None)`. An empty input
dictionary  `{}` would result in an object with the default value `some_var = None`, but the input dictionary `{"some_var": None}` itself
would **not** be valid at all.

Instead, to explicitly allow `None` as value, you can use the `Noneable` meta validator (introduced [earlier](03-basic-validators.md)),
e.g. `some_var: Optional[int] = Noneable(IntegerValidator())`. This however does **not** make the field optional, so an input dictionary
with the value `None` would be allowed, but omitting the field in an input dictionary would be invalid.

To make a field both optional **and** allow `None` as value, you can simply combine `Noneable()` and a `Default` value. \
For example: `some_var: Optional[int] = Noneable(IntegerValidator()), Default(None)`.

You can also configure the `Noneable` meta validator to use a different default value than `None`. For example, to always use `0` as the
default value, regardless of whether the field is missing in the input dictionary or whether the field has the input value `None`: \
`some_var: int = Noneable(IntegerValidator(), default=0), Default(0)`.


## Post-validation

Post-validation is everything that happens **after** all fields have been validated individually, but **before** the `DataclassValidator`
returns the dataclass object.

For example, you could implement additional validation criteria that depend on the values of multiple fields of the dataclass. One common
use case for this are fields that are optional by default, but can be **required** under certain conditions, e.g. fields A and B are not
required, but if one of them exists, the other must exist too (or conversely, only one of the fields is allowed to be set at the same
time).

Another use case are "integrity constraints". Imagine you have a dataclass with two datetime fields `begin_time` and `end_time` that
specify the start and end of a time interval. You might want to ensure that `begin_time <= end_time` is always true, because a time
interval cannot end before it starts. This cannot be done using the field validators alone, so you need to do this integrity check
**post validation**.

Of course, you can do any sort of post-validation on a validated object after is was returned by the `DataclassValidator`. But a more
elegant way is to **integrate** the post-validation logic into the validator and/or dataclass itself.

There are two ways to do this: One way is to **subclass** the `DataclassValidator` for your dataclass and override the `post_validate()`
method (which by default doesn't do anything with the object). Another way is to use the `__post_init__()` special method of dataclasses.
We will only demonstrate the latter for now, because it's a bit more easy (doesn't require subclassing the validator).

Dataclasses can have the special method `__post_init__()` which will be automatically called after the `__init__()` special method.
It does not receive any arguments (unless so called `InitVar` fields are used, which are currently unsupported by this library), but it
can access the objects fields as usual with `self.field_name`.

Let's see how this can be done for the datetime example from above:

```python
from datetime import datetime

from validataclass.exceptions import ValidationError
from validataclass.helpers import validataclass
from validataclass.validators import DataclassValidator, DateTimeValidator, DateTimeFormat

@validataclass
class ExampleClass:
    # Two datetime fields (UTC only, for simplicity)
    begin_time: datetime = DateTimeValidator(DateTimeFormat.REQUIRE_UTC)
    end_time: datetime = DateTimeValidator(DateTimeFormat.REQUIRE_UTC)

    def __post_init__(self):
        # Ensure that begin_time is always before end_time
        if self.begin_time > self.end_time:
            raise ValidationError(
                code='invalid_interval',
                reason='Field "begin_time" must not be greater than "end_time".'
            )

# Create a validator for this dataclass
validator = DataclassValidator(ExampleClass)

# Valid example: Will return a valid ExampleClass object
validator.validate({"begin_time": "2021-10-21T15:00:00Z", "end_time": "2021-10-21T16:00:00Z"})

# Invalid example: Will raise a DataclassPostValidationError
validator.validate({"begin_time": "2021-10-21T15:00:00Z", "end_time": "2021-10-21T14:00:00Z"})
```


### Post-validation errors

To raise a validation error, we can simply use `raise ValidationError( ... )` in the `__post_init__()` method. This can be an arbitrary
exception, but it's recommended to use `ValidationError`, any of the built-in subclasses, or to create your own `ValidationError` subclass.

The `DataclassValidator` will automatically **wrap** this exception in a `DataclassPostValidationError` (similar to how field errors are
wrapped in a `DictFieldsValidationError`), unless the exception already is an exception of this type, then it is re-raised unmodified.
A `DataclassPostValidationError` can also contain multiple validation errors, which are then mapped to individual fields. See the
[docstrings of `DataclassPostValidationError`](../src/validataclass/exceptions/dataclass_exceptions.py) for further details. 

Converting the `DataclassPostValidationError` of the example above to a dictionary using `.to_dict()` will result in the following
dictionary:

```pycon
{
    'code': 'post_validation_errors',
    'error': {
        'code': 'invalid_interval',
        'reason': 'Field "begin_time" must not be greater than "end_time".'
    }
}
```


### Conditionally required fields

Here is another code example for a dataclass with conditionally required fields:

```python
from typing import Optional

from validataclass.exceptions import RequiredValueError, DataclassPostValidationError
from validataclass.helpers import validataclass, Default
from validataclass.validators import DataclassValidator, BooleanValidator, IntegerValidator

@validataclass
class ExampleClass:
    # This field is always required
    enable_something: bool = BooleanValidator()
    
    # This field is required only if enable_something is True. Otherwise it will be ignored.
    some_value: Optional[int] = IntegerValidator(), Default(None)

    def __post_init__(self):
        # If enable_something is True, ensure that some_value is set!
        if self.enable_something is True and self.some_value is None:
            raise DataclassPostValidationError(field_errors={
                'some_value': RequiredValueError(reason='Must be set if enable_something is True.'),
            })

# Create a validator for this dataclass
validator = DataclassValidator(ExampleClass)

# Valid examples: Will return valid ExampleClass objects
validator.validate({"enable_something": False})                   # -> ExampleClass(enable_something=False, some_value=None)
validator.validate({"enable_something": True, "some_value": 42})  # -> ExampleClass(enable_something=True, some_value=42)

# Invalid example: Will raise a DataclassPostValidationError
validator.validate({"enable_something": True})
```

The `DataclassPostValidationError` from this example will look like this after converting it to a dictionary:

```pycon
{
    'code': 'post_validation_errors', 
    'field_errors': {
        'some_value': {
            'code': 'required_value',
            'reason': 'Must be set if enable_something is True.'
        }
    }
}
```


### Post-initialization variables

Another thing you can do at post-validation time is setting "post-initialization fields". These are fields in a dataclass that are
**not** set at initialization yet (i.e. not set in `__init__()`), but after initialization (in `__post_init__()`). In the context
of our validators this means that the variable is **not part of the input dictionary**.

These fields can be defined using `field(init=False)`. This requires the regular `field()` function from dataclasses and cannot be done
using `validataclass_field()`, for the simple reason that those fields are not validated.

The following example defines a dataclass with two **validated** integer fields `value1` and `value2`, and a third **post-init** field
called `sum`. This field is not part of input dictionaries, and will be set to the sum of `value1` and `value2` in `__post_init__()`.

```python
from dataclasses import field

from validataclass.helpers import validataclass
from validataclass.validators import DataclassValidator, IntegerValidator

@validataclass
class ExampleClass:
    value1: int = IntegerValidator()
    value2: int = IntegerValidator()
    
    sum: int = field(init=False)

    def __post_init__(self):
        # Set post-init field "sum" to the sum of value1 and value2
        self.sum = self.value1 + self.value2

# Test the validator
validator = DataclassValidator(ExampleClass)
validator.validate({'value1': 13, 'value2': 29})  # -> ExampleClass(value1=13, value2=29, sum=42)
validator.validate({'value1': -3, 'value2': 3})   # -> ExampleClass(value1=-3, value2=3, sum=0)

# Setting the "sum" field in the input dictionary will not have any effect,
# since the DataclassValidator does not know this field and therefore ignores it.
validator.validate({'value1': 1, 'value2': 2, 'sum': 99})  # -> ExampleClass(value1=1, value2=2, sum=3)
```


## Extensive example with nested dataclasses

In conclusion, let's take a look at a final example. This one is a bit more extensive than the ones before, it even has
**nested dataclasses**, an Enum class, and a post-validation check.


```python
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from validataclass.exceptions import ValidationError, DataclassPostValidationError
from validataclass.helpers import validataclass, Default
from validataclass.validators import DataclassValidator, ListValidator, IntegerValidator, StringValidator, DecimalValidator, \
    EnumValidator, DateTimeValidator

class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'

@validataclass
class OrderItem:
    name: str = StringValidator()
    price: Decimal = DecimalValidator()
    color: Optional[Color] = EnumValidator(Color), Default(None)

@validataclass
class Order:
    id: int = IntegerValidator()
    items: List[OrderItem] = ListValidator(DataclassValidator(OrderItem))
    total_price: Decimal = DecimalValidator()
    ordered_at: datetime = DateTimeValidator()

    def __post_init__(self):
        # Ensure that "total_price" is the correct sum of all item prices
        calculated_sum = sum(item.price for item in self.items)
        if self.total_price != calculated_sum:
            raise DataclassPostValidationError(field_errors={
                'total_price': ValidationError(code='invalid_sum'),
            })


# Now, let's validate some input with these dataclasses!
validator = DataclassValidator(Order)

input_data = {
    'id': 123,
    'items': [
        {
            'name': 'banana',
            'price': '1.23',
            'color': 'yellow',
        },
        {
            'name': 'apple',
            'price': '0.62',
        },
    ],
    'total_price': '1.85',
    'ordered_at': '2021-07-01T12:34:56Z',
}

validated_order = validator.validate(input_data)
print(validated_order)

for item in validated_order.items:
    print(f"Item: {item.name} for {item.price} money units")
```

This code will output (formatted for better readability):

```text
Order(
    id=123,
    items=[
        OrderItem(name='banana', price=Decimal('1.23'), color=<Color.YELLOW: 'yellow'>),
        OrderItem(name='apple',  price=Decimal('0.62'), color=None)
    ],
    total_price=Decimal('1.85'),
    ordered_at=datetime.datetime(2021, 7, 1, 12, 34, 56, tzinfo=datetime.timezone.utc)
)

Item: banana for 1.23 money units
Item: apple for 0.62 money units
```


## Summary

In this chapter we have learned how to leverage dictionary validation using dataclasses, the `@validataclass` decorator and the
`DataclassValidator`.

This basically concludes most of our tour of this library, except for one additional chapter: How to [build your own
validators](06-build-your-own.md) (or extend existing validators).
