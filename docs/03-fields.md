## Fields

Fields can be used in inputs


### BaseField

When you initialize a field you can set following args / kwargs:

* `input_filters` are a list of filters which run before validating the data
* `output_filters` are a list of filters which run after validation for `out` property
* `validators` are a list of validators which are triggered by an input validation. Most fields have pre-defined validators like a type validation.
* `required` is a boolean which states if the field is required or not. If it's not required, it's ok if the field is unset, but it will thorow an error if you provide an null / undefined / emptystring

Usually, you don't need properties and methods of single fields, maybe except for `data` which is a good way for post-validation-handling like:

```python
my_field_data = form.field.data
```


### Type fields

wtfjson provides several fields which are basicly python data types:

* BooleanField
* DateField
* DateTimeField
* DecimalField
* EnumField
* FloatField
* IntegerField
* StringField

### DictField

A `ObjectField` is basicly a sub-object which expects another Form as sub-object.

### ListField

A `ListField` is basicly a sub-list which expects a sub-field and `min_entries` / `max_entries` as optional parameter.

