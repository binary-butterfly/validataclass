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
This makes it difficult for type checkers or code linters (including IDEs like PyCharm) to analyse the code that's working with the
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

from validataclass.dataclasses import validataclass_field
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
tuples can also be used to specify a field default (explained later). In most other cases (including when a class variable has no value
set at all), the decorator will raise an exception.

Here is our dataclass example again, now using the `@validataclass` decorator:

```python
from decimal import Decimal

from validataclass.dataclasses import validataclass
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

While dataclasses have built-in support for field default values, they unfortunately have a rather impractical
restriction on the order of fields: In a dataclass, all optional fields (i.e. fields with default values) must be
defined **after** all of the required fields. Defining a required field (i.e. a field without default value) after an
optional field will result in an error:

```python
from dataclasses import dataclass

@dataclass
class ExampleDataclass:
    var1: int
    var2: str = 'some default value'
    var3: int  # This raises a TypeError because the field has no default value!
```

In this example, you would either have to move the `var3` field above `var2` or define a default for `var3`.

To circumvent this restriction, we first opted to implement our own default value handling in the `DataclassValidator`.
Like the field validators, the field defaults are stored in the **metadata** of the field, namely under the key
`"validator_default"`. The `DataclassValidator` will then fill the missing fields in the input dictionary with these
default values before attempting to create dataclass objects.

This first implementation was far from perfect, though (namely, you couldn't simply use a validataclass in the same way
as a regular dataclass because (from a regular dataclass perspective) the fields didn't have any defaults and thus were
all required).

Starting with validataclass 0.6.0, fields now also have proper dataclass field defaults. The `DataclassValidator` will
still use the defaults stored in the field metadata, but you can now also create objects from a validataclass using
default values in the same way as with a regular dataclass.

This is accomplished by creating dataclasses with the option `kw_only=True` (which modifies the auto-generated class
constructor to only accept keyword arguments, so that the order of arguments doesn't matter anymore). This option was
only introduced in Python 3.10, though, so for older versions of Python a slightly hacky workaround was implemented
(take a look at the code of `validataclass_field()` if you're curious).

In general, all fields that do **not** have any default value are required fields (i.e. `DataclassValidator` will reject
any input where one of these fields is missing). To define an optional field **without** a default value, you can use
the special `DefaultUnset` object (which is explained later).

Of course, both the `validataclass_field()` function and the `@validataclass` decorator can be used to conveniently set
default values for fields.


### Setting defaults with `validataclass_field()`

To set a default value with `validataclass_field()`, you simply specify the `default` parameter. This parameter can be
set either to a `Default` object (which we will explain in a moment) or directly to a value.

**Example:**

```python
from dataclasses import dataclass

from validataclass.dataclasses import validataclass_field, Default
from validataclass.validators import IntegerValidator

@dataclass
class ExampleDataclass:
    # The following fields are equivalent
    field_a: int = validataclass_field(IntegerValidator(), default=42)           # Specify default as direct value
    field_b: int = validataclass_field(IntegerValidator(), default=Default(42))  # Specify default using a Default object
```


### Setting defaults with `@validataclass`

To set a default value for a field using the `@validataclass` decorator, you have to define the field as a **tuple**
consisting of the validator and a `Default` object, e.g. `IntegerValidator(), Default(42)`.

Please note that in Python 3.7 for some reason these tuples require parentheses (see example). Unless you're writing
code for Python 3.7, it is recommended to omit the parentheses for a more consistent look, though.

**Example:**

```python
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import IntegerValidator

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
`DefaultFactory(lambda: some_list)` as default for a dataclass field, all objects validated using this dataclass will use **the same**
list as their default. Modifying the list of one validated object will modify the list for **all** objects.


#### DefaultUnset and the `UnsetValue` object

If you set a default value for a field in a dataclass, this field will **always** have a value: Either the value from the input dictionary
if the field exists, or the default value. If you don't set a default value, the field is **required**, meaning an input dictionary
without this field will fail validation.

Sometimes you want optional fields **without** default values though: If a string field uses `Default('')` for example, it will always
have a string value (either empty or not empty), and you cannot distinguish whether the field was omitted in the input dictionary or
whether the user explicitly set the field to an empty string.

One solution is to use `Default(None)` instead: If the field is `None`, you know that the field did not exist in the input dictionary.

This is sufficient in a lot of cases, but sometimes `None` is an allowed value for a field (e.g. when using the `Noneable`
wrapper) and you need to distinguish between "the field did not exist" and "the field was explicitly set to `None`".

For this case, we defined a special value called `UnsetValue`, which you can use similarly to `None`. These values are so called
[sentinel objects](https://python-patterns.guide/python/sentinel-object/): Their purpose is to represent a missing value. They also are
unique objects, which means you cannot copy them: Trying to create a new object using `UnsetValue()` or even using `deepcopy(UnsetValue)`
will always result in a reference to the **same** object. This ensures that you can check for this value using the identity operator `is`,
e.g. `if some_value is UnsetValue` (just like `is None` or `is True`).

So, to define an **optional field without default** you can simply specify `UnsetValue` as the default value, and then use `is UnsetValue`
in your code to distinguish it from other values like `None`.

For this you can use the `DefaultUnset` object, which is a shortcut for `Default(UnsetValue)`.

Remember to adjust the type hints in your dataclass though. There is a type alias `OptionalUnset[T]` which you can use for this, for
example: `some_var: OptionalUnset[int]`, which is equivalent to `Union[int, UnsetValueType]`. For fields that can be both `None` and
`UnsetValue`, there is also the type alias `OptionalUnsetNone[T]` as a shortcut for `OptionalUnset[Optional[T]]`.


#### NoDefault

Specifying the `NoDefault` object for a field default literally means that the field does not have any default value. This is equivalent
to **not specifying a default value at all**, meaning the field will be **required** and not optional.

In most cases you won't need this value, but it can be useful to overwrite an existing default in a subclass (see the "Subclassing"
section below).


#### Examples for the various Default classes

The following code contains examples for all the various `Default` classes that we've seen above.

```python
from datetime import datetime
from typing import Optional

from validataclass.dataclasses import validataclass, Default, DefaultFactory, DefaultUnset, NoDefault
from validataclass.helpers import OptionalUnset
from validataclass.validators import IntegerValidator, ListValidator, DateTimeValidator

@validataclass
class ExampleClass:
    # Simple defaults for integer fields
    field_a: int = IntegerValidator(), Default(42)                  # Default value is 42
    field_b: Optional[int] = IntegerValidator(), Default(None)      # Default value is None
    field_c: OptionalUnset[int] = IntegerValidator(), DefaultUnset  # Default value is UnsetValue

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

Instead, to explicitly allow `None` as value, you can use the `Noneable` wrapper (introduced [earlier](03-basic-validators.md)),
e.g. `some_var: Optional[int] = Noneable(IntegerValidator())`. This however does **not** make the field optional, so an input dictionary
with the value `None` would be allowed, but omitting the field in an input dictionary would be invalid.

To make a field both optional **and** allow `None` as value, you can simply combine `Noneable()` and a `Default` value. \
For example: `some_var: Optional[int] = Noneable(IntegerValidator()), Default(None)`.

You can also configure the `Noneable` wrapper to use a different default value than `None`. For example, to always use `0` as the
default value, regardless of whether the field is missing in the input dictionary or whether the field has the input value `None`: \
`some_var: int = Noneable(IntegerValidator(), default=0), Default(0)`.


## Subclassing

The `@validataclass` decorator also supports class inheritance to extend or modify dataclasses. For example, you can add new fields to
a dataclass, set different default values for fields and even change the field validators.

This is useful if you have multiple similar dataclasses. Instead of repeating all field validators in all dataclasses, you can define
a base dataclass and multiple subclasses derived from it.

For example, if your dataclasses all share a certain set of fields, you can define a base class with these common fields:

```python
from decimal import Decimal

from validataclass.dataclasses import validataclass
from validataclass.validators import IntegerValidator, StringValidator, DecimalValidator

@validataclass
class BaseClass:
    # Common fields used in all requests
    name: str = StringValidator()
    some_value: int = IntegerValidator()

@validataclass
class SubClass(BaseClass):
    # Fields only used in a specific request
    some_decimal: Decimal = DecimalValidator()
```

With the `BaseClass` from this example you could validate dictionaries that consist only of the two keys `name` and `some_value`, while
the `SubClass` has the same `name` and `some_value` fields but an additional field `some_decimal`.

You can also overwrite the validators and/or default values for existing fields. To do this, simply specify the new validator and/or
default value. Not specifying a new validator or default value will keep the existing one, so you can for example set a new default value
for a field without repeating the validator.

For example, imagine you have two dataclasses for two different API requests, one for creating some resource and one for modifying an
existing one. When creating a resource, you might want to make all fields mandatory (or define certain default values for them),
because you need to set the values of the resource to something. But when modifying a resource, you might want to make all fields
optional (using `UnsetValue` as the default) and only change the values that are present in the request. You could do this by deriving
the "modify" dataclass from the "create" dataclass and change all field defaults to `DefaultUnset`:

```python
from decimal import Decimal
from typing import Optional

from validataclass.dataclasses import validataclass, Default, DefaultUnset
from validataclass.helpers import OptionalUnset, OptionalUnsetNone
from validataclass.validators import IntegerValidator, StringValidator, DecimalValidator

@validataclass
class CreateStuffRequest:
    name: str = StringValidator()
    some_value: int = IntegerValidator()
    some_decimal: Optional[Decimal] = DecimalValidator(), Default(None)

@validataclass
class ModifyStuffRequest(CreateStuffRequest):
    # Set all field defaults to DefaultUnset
    name: OptionalUnset[str] = DefaultUnset
    some_value: OptionalUnset[int] = DefaultUnset
    some_decimal: OptionalUnsetNone[Decimal] = DefaultUnset
```

As you can see here, no validators are specified in the subclass, so the `DataclassValidator` will use the same validators as for the
base class.

Conversely, you can specify a new validator for a field without changing an existing default value. To remove an existing default value
and make an optional field required, you can simply specify `NoDefault` (e.g. `some_decimal: Decimal = NoDefault`).

Multiple inheritance (i.e. having a class with more than one parent) is also supported and can be used to create **mixins**
that you can re-use in your validataclasses, even if they already inherit from another base class:

```python
from decimal import Decimal

from validataclass.dataclasses import validataclass, Default
from validataclass.validators import IntegerValidator, StringValidator, DecimalValidator

@validataclass
class BaseA:
    field_a: int = IntegerValidator(), Default(0)

@validataclass
class BaseB:  # Note: This is NOT a subclass of BaseA
    field_b: str = StringValidator()

@validataclass
class SubClass(BaseB, BaseA):
    # SubClass will have "field_a" from BaseA, "field_b" from BaseB, and a new field "field_c"
    field_c: Decimal = DecimalValidator()

    # You can also override validator and/or default as described above:
    field_a: int = Default(42)
```

There is one important caveat about multiple inheritance: If two **unrelated** base classes of your dataclass define a
field with the same name, the base class that is higher in the MRO (Method Resolution Order) takes full precendence over
the other. Contrary to regular inheritance (e.g. a subclass overrides only the default of a field) there are no partial
overrides in this case. In the following example, `SubClass` will have the field `field_both` as defined in `BaseB`, so
it's a `StringValidator` **without** a default value:

```python
from validataclass.dataclasses import validataclass, Default
from validataclass.validators import IntegerValidator, StringValidator

@validataclass
class BaseA:
    field_both: int = IntegerValidator(), Default(42)

@validataclass
class BaseB:  # Note: This is NOT a subclass of BaseA
    field_both: str = StringValidator()

@validataclass
class SubClass(BaseB, BaseA):
    # Note: The left-most base class (BaseB) takes precendence over other base classes.
    pass
```


## Post-validation

Post-validation is everything that happens **after** all fields have been validated individually, but **before** the
`DataclassValidator` returns the dataclass object.

For example, you could implement additional validation criteria that depend on the values of multiple fields of the
dataclass. One common use case for this are fields that are optional by default, but can be **required** under certain
conditions, e.g. fields A and B are not required, but if one of them exists, the other must exist too (or conversely,
only one of the fields is allowed to be set at the same time).

Another use case are "integrity constraints". Imagine you have a dataclass with two datetime fields `begin_time` and
`end_time` that specify the start and end of a time interval. You might want to ensure that `begin_time <= end_time` is
always true, because a time interval cannot end before it starts. This cannot be done using the field validators alone,
so you need to do this integrity check **post validation**.

Of course, you can do any sort of post-validation on a validated object after it was returned by the `DataclassValidator`.
But a more elegant way is to **integrate** the post-validation logic into the `DataclassValidator` and dataclass itself.

There are two ways to implement post-validation in a validataclass: First, there is the `__post_init__()` special method
which is automatically called as part of the `__init__()` method of a dataclass. It is a feature of regular dataclasses,
so this post-validation is also applied when instantiating the dataclass without using validataclass.

The other way is to implement the `__post_validate__()` method. This method is called by the `DataclassValidator` right
after creating the object. It is a feature of validataclass, so it is **not** called when instantiating the dataclass
manually (although you can of course just call `obj.__post_validate__()` manually as well).

The `__post_validate__()` method additionally supports another special feature: **context-sensitive validation**, which
will be discussed shortly.

This example implements the datetime post-validation example from above:

```python
from datetime import datetime

from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator, DateTimeValidator, DateTimeFormat

@validataclass
class ExampleClass:
    # Two datetime fields (UTC only, for simplicity)
    begin_time: datetime = DateTimeValidator(DateTimeFormat.REQUIRE_UTC)
    end_time: datetime = DateTimeValidator(DateTimeFormat.REQUIRE_UTC)

    # Note: In this case, __post_init__() would look exactly the same.
    def __post_validate__(self):
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

from validataclass.dataclasses import validataclass, Default
from validataclass.exceptions import RequiredValueError, DataclassPostValidationError
from validataclass.validators import DataclassValidator, BooleanValidator, IntegerValidator

@validataclass
class ExampleClass:
    # This field is always required
    enable_something: bool = BooleanValidator()

    # This field is required only if enable_something is True. Otherwise it will be ignored.
    some_value: Optional[int] = IntegerValidator(), Default(None)

    def __post_validate__(self):
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


### Context-sensitive post-validation

As mentioned earlier, the `__post_validate__()` method supports a nice feature called **context-sensitive validation**.

In general, this means that the validation can depend on the **context** it is used in. Usually, the output of a
validator is always determined by a) the options set at the time the validator was created and b) the input value.
Context-sensitive validation means that you pass additional parameters to the validator at runtime, i.e. at the time
the `validate()` method is called to validate a piece of input.

These so called **context arguments** are passed to the `validate()` call as arbitrary keyword arguments. Whether and
how the validator actually uses these arguments depends on the implementation of the validator. Most validators don't
do anything with it except for passing it to sub-validators (e.g. the `ListValidator` passes the context arguments to
the specified item validator).

The `DataclassValidator` supports these context arguments and uses them in two ways: First, it passes them as they are
to any field validator (which might pass them to other validators as well). Second, it also passes them to the
`__post_validate__()` method of the dataclass as long as the method accepts them.

You can define the `__post_validate__()` method with specific keyword-only arguments and/or with a `**kwargs` parameter.
The `DataclassValidator` will make sure to only pass the arguments that the method accepts. Please make sure to use
**keyword-only** arguments instead of positional arguments. The latter will still work, but emit a warning.

Example:

```python
from typing import Optional

from validataclass.dataclasses import validataclass, Default
from validataclass.exceptions import RequiredValueError, DataclassPostValidationError
from validataclass.validators import DataclassValidator, BooleanValidator, IntegerValidator

@validataclass
class ContextSensitiveExampleClass:
    # This field is optional, unless the context says otherwise.
    some_value: Optional[int] = IntegerValidator(), Default(None)

    # Note: You can also specify **kwargs here to get all context arguments.
    def __post_validate__(self, *, require_some_value: bool = False):
        # If require_some_value was set at validation time, ensure that some_value is set!
        if require_some_value and self.some_value is None:
            raise DataclassPostValidationError(field_errors={
                'some_value': RequiredValueError(reason='Must be set in this context.'),
            })

# Create a validator for this dataclass
validator = DataclassValidator(ContextSensitiveExampleClass)

# Without context arguments: The field is optional.
validator.validate({})                  # -> ContextSensitiveExampleClass(some_value=None)
validator.validate({"some_value": 42})  # -> ContextSensitiveExampleClass(some_value=42)

# With the context argument "require_some_value" set: The field is now required!
validator.validate({}, require_some_value=True)                  # will raise a DataclassPostValidationError
validator.validate({"some_value": 42}, require_some_value=True)  # -> ContextSensitiveExampleClass(some_value=42)
```

**One important note about the `validate()` method:**

For backwards compatibility, `Validator` classes currently are **not** required to accept arbitrary keyword arguments.
Custom validators that were created before this feature was implemented (version 0.7.0) will not support this, so
calling their `validate()` method with keyword arguments will raise an error.

To avoid this, there is a helper method that wraps the `validate()` call: `Validator.validate_with_context()` will check
whether the validator class supports context arguments, then call the `validate()` method either with or without them.

In cases where you don't know whether your validator class already supports context arguments (especially when writing
generic code that can use arbitrary validators), you should therefore use the `validate_with_context()` method.

Example:

```python
from validataclass.validators import Validator

validator: Validator = ...  # This can be any validator class
input_data = ...

validated_data = validator.validate_with_context(input_data, my_context_var=42)
```

This method will become obsolete and eventually removed in the future (possibly in version 1.0.0), when every validator
class will be required to support context arguments.

**Therefore, you should upgrade your custom validator classes to support context arguments, and also to pass them to
any underlying base validator.**

To do this, simply add a `**kwargs` argument to your `validate()` call. For example:

```python
from typing import Any
from validataclass.validators import StringValidator

class UppercaseStringValidator(StringValidator):
    # BEFORE:
    # def validate(self, input_data: Any) -> str:
    #     validated_str = super().validate(input_data)
    #     return validated_str.upper()

    # AFTER:
    def validate(self, input_data: Any, **kwargs) -> str:
        validated_str = super().validate(input_data, **kwargs)
        return validated_str.upper()
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

from validataclass.dataclasses import validataclass
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

from validataclass.dataclasses import validataclass, Default
from validataclass.exceptions import ValidationError, DataclassPostValidationError
from validataclass.validators import DataclassValidator, ListValidator, IntegerValidator, StringValidator, \
    DecimalValidator, EnumValidator, DateTimeValidator

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
