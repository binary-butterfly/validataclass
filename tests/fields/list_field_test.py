# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import DictInput
from wtfjson.fields import StringField, ListField


class StringListDictInput(DictInput):
    test_field = ListField(StringField())


class ListInListDictInput(DictInput):
    test_field = ListField(ListField(StringField()))


class ListFieldTest(TestCase):
    def test_success(self):
        form = StringListDictInput(data={'test_field': ['keks', 'lecker']})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': ['keks', 'lecker']}

    def test_no_list(self):
        form = StringListDictInput(data={'test_field': 'nanana'})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field': ['invalid type']}

    def test_wrong_list_entry(self):
        form = StringListDictInput(data={'test_field': ['keks', 123]})
        assert form.validate() is False
        assert form.has_errors is True
        assert form.errors == {'test_field.1': ['invalid type']}

    def test_list_in_list(self):
        form = ListInListDictInput(data={'test_field': [['cookie', 'banana'], ['cake', 'strawberry']]})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        assert form.out == {'test_field': [['cookie', 'banana'], ['cake', 'strawberry']]}
