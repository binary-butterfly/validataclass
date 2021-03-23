# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Optional
from unittest import TestCase
from dataclasses import dataclass
from wtfjson import DictInput
from wtfjson.fields import StringField


class PopulateDictInput(DictInput):
    test_field = StringField()


class RenamePopulateDictInput(DictInput):
    test_field_renamed = StringField(populate_to='test_field')


@dataclass
class TestClass:
    test_field: Optional[str] = None


class PopulateToTest(TestCase):
    def test_success(self):
        form = PopulateDictInput(data={'test_field': 'cookie'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        test_class = TestClass()
        form.populate_obj(test_class)
        assert test_class.test_field == 'cookie'

    def test_success_rename(self):
        form = RenamePopulateDictInput(data={'test_field_renamed': 'cookie'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        test_class = TestClass()
        form.populate_obj(test_class)
        assert test_class.test_field == 'cookie'
