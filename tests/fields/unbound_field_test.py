# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from wtfjson import ListInput, DictInput
from wtfjson.fields import StringField, ObjectField, UnboundField


class TestDictInput(DictInput):
    field = StringField()


class StringListInput(ListInput):
    field = StringField()


class ObjectForListInput(DictInput):
    field = StringField()


class ObjectListInput(ListInput):
    field = ObjectField(ObjectForListInput)


class UnboundFieldTest(TestCase):
    def test_dict_input(self):
        assert type(TestDictInput.field) is UnboundField
        form = TestDictInput({'field': 'test'})
        assert type(form.field) is StringField

    def test_list_input(self):
        assert type(StringListInput.field) is UnboundField
        form = StringListInput(['string'])
        assert type(form._fields[0]) is StringField
