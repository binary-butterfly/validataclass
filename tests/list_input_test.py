# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import ListInput, DictInput
from wtfjson.fields import StringField, ObjectField


class StringListInput(ListInput):
    field = StringField()


class ObjectForListInput(DictInput):
    field = StringField()


class ObjectListInput(ListInput):
    field = ObjectField(ObjectForListInput)


class ListInputTest(TestCase):
    def test_success(self):
        form = StringListInput(['keks', 'lecker'])
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == ['keks', 'lecker']

    def test_success_object(self):
        form = ObjectListInput([{'field': 'keks'}])
        form.validate()
        print(form.errors)
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == [{'field': 'keks'}]

    def test_success_object_multible(self):
        form = ObjectListInput([{'field': 'keks'}, {'field': 'lecker'}])
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        print(form.out)
        assert form.out == [{'field': 'keks'}, {'field': 'lecker'}]

    def test_no_list(self):
        form = StringListInput('cookie')
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'_root': ['invalid type']}

    def test_wrong_list_entry(self):
        form = StringListInput(['keks', 123])
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'1': ['invalid type']}
