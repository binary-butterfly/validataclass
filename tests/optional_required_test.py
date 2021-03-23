# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import IntegerField, StringField, ListField
from wtfjson.validators import Length, NumberRange


class OptionalDictInput(DictInput):
    test_field = IntegerField(
        required=False,
        validators=[
            NumberRange(min=1)
        ]
    )


class OptionalListDictInput(DictInput):
    test_field = ListField(
        StringField(
            validators=[
                Length(min=1)
            ]
        ),
        required=False
    )


class RequiredDictInput(DictInput):
    test_field = StringField(
        validators=[
            Length(min=1)
        ]
    )


class OptionalRequiredTest(TestCase):
    def test_optional(self):
        form = OptionalDictInput(data={})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {}

    def test_optional_list(self):
        form = OptionalListDictInput(data={})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {}

    def test_optional_list_empty_data(self):
        form = OptionalListDictInput(data={'test_field': []})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': []}

    def test_optional_list_data(self):
        form = OptionalListDictInput(data={'test_field': ['cookie', 'cupcake']})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': ['cookie', 'cupcake']}

    def test_optional_data(self):
        form = OptionalDictInput(data={'test_field': 1})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': 1}

    def test_optional_invalid_data(self):
        form = OptionalDictInput(data={'test_field': 'str'})
        assert form.validate() is False
        assert form.has_errors is True
        print(form.errors)

    def test_required_error(self):
        form = RequiredDictInput(data={})
        assert form.validate() is False
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['data required']}

    def test_required_success(self):
        form = RequiredDictInput(data={'test_field': 'cookies'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': 'cookies'}
