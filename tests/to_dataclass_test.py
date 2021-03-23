# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest import TestCase
from dataclasses import dataclass
from wtfjson import DictInput
from wtfjson.fields import StringField


class PopulateDictInput(DictInput):
    test_field = StringField()


@dataclass
class TestClass:
    test_field: str


@dataclass
class TestClassFrom:
    @classmethod
    def from_dict(cls, **data):
        data['test_field'] += 's'
        return cls(**data)

    test_field: str


class ToDataclassTest(TestCase):
    def test_success(self):
        form = PopulateDictInput(data={'test_field': 'cookie'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        test_class = form.to_dataclass(TestClass)
        assert test_class.test_field == 'cookie'

    def test_success_from(self):
        form = PopulateDictInput(data={'test_field': 'cookie'})
        assert form.validate() is True
        assert form.has_errors is False
        assert form.errors == {}
        test_class = form.to_dataclass(TestClassFrom)
        assert test_class.test_field == 'cookies'
