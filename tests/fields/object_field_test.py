# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import StringField, ObjectField, IntegerField


class SubObjectDictInput(DictInput):
    test_field_string = StringField()
    test_field_int = IntegerField()


class ObjectDictInput(DictInput):
    test_field = ObjectField(SubObjectDictInput)


class ObjectFieldTest(TestCase):
    def test_success(self):
        form = ObjectDictInput(data={'test_field': {'test_field_string': 'lecker', 'test_field_int': 10}})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': {'test_field_string': 'lecker', 'test_field_int': 10}}

    def test_no_object(self):
        form = ObjectDictInput(data={'test_field': 'nanana'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}

    def test_invalid_sub_field(self):
        form = ObjectDictInput(data={'test_field': {'test_field_string': 'lecker', 'test_field_int': '10'}})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field.test_field_int': ['invalid type']}
