## Inputs

The entry point for any data is DictInput or ListInput. It basicly a class which handles all fields in it.


### DictInput

A `DictInput` is a base class for JSON objects and therefore has named fields. It basicly looks like this:

```python
class MyDictInput(DictInput):
    field1 = DataType1()
    field2 = DataType2()
```

### ListInput

A `ListInput` is a base class for JSON arrays and therefore has a list of fields. It basicly looks like this (the property `field` is fixed):

```python
class MyListInput(ListInput):
    field = DataType1()
```

### using inputs

You can load data into an input by initializing the class:

```python
form = MyDictInput(my_input_dict)
```

Afterwards you can (and must!) validate the data. You will get True vor valid or False for invalid back: 

```python
form.validate()
```

If there are any errors, you can access them with the attribute `.errors`. Additional, the property `.has_errors` is True. 

If the Input is valid you can access data with attributes `.data` (before output filters) and `.out` (after output filters).

You can also access the raw fields by `form.field1` in case of an DictInput.

Additionally, you can copy all data to another object (which is really helpful for dataclass-based update objects or SQLAlchemy-objects) by:

```python
form.populate_obj(another_object)
```

