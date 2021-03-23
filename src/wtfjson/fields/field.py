# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC
from enum import Enum
from copy import deepcopy
from typing import List, Callable, Optional, Any

from ..abstract_input import AbstractInput
from ..util import unset_value
from ..exceptions import ValidationError, StopValidation, ClearValidation
from .unbound_field import UnboundField


class FieldState(Enum):
    initialized = 1
    processed = 2
    loaded = 3
    validated = 4


class Field(ABC):
    state: FieldState
    _form: AbstractInput
    _field_name: str
    data_raw: Any  # raw input data
    data_processed: Any  # data after input filters
    data_out: Any  # data after output filters
    description: Optional[str]
    input_filters: Optional[List[Callable]]
    default_input_filters: List[Callable] = []
    output_filters: Optional[List[Callable]]
    default_output_filters = List[Callable]
    validators: Optional[list]
    default_validators: list = []
    pre_validators: list = []
    validation_stopped: bool
    _errors: dict
    required: bool

    def __init__(self,
                 form: AbstractInput = None,
                 field_name: str = None,
                 description: Optional[str] = None,
                 input_filters: Optional[list] = None,
                 output_filters: Optional[list] = None,
                 validators: Optional[list] = None,
                 required: bool = True,
                 populate_to: Optional[str] = None):
        self.description = description
        self.input_filters = input_filters if input_filters is not None else []
        self.output_filters = output_filters if output_filters is not None else []
        self.validators = validators if validators is not None else []
        self.required = required
        self.populate_to = populate_to

        self._errors = {}
        self._form = form
        self._field_name = field_name
        self.state = FieldState.initialized
        self.data_raw = unset_value
        self.data_processed = unset_value
        self.data_out = unset_value
        self.validation_stopped = False

    def __new__(cls, *args, **kwargs):
        if "form" in kwargs:
            return super().__new__(cls)
        else:
            return UnboundField(cls, *args, **kwargs)

    def process_in(self, data_raw: Any, remove_none: bool = False):
        """
        after initializing the form the data is added in a raw form and is processed afterwards
        """
        self.data_raw = deepcopy(data_raw)
        self.data_processed = deepcopy(self.data_raw)
        for input_filter in self.default_input_filters + self.input_filters:
            self.data_processed = input_filter(self.data_processed)
        self.state = FieldState.processed
        self.pre_validate()

    def pre_validate(self):
        """
        this validator runs before turning data into objects / lists / ...
        """
        try:
            for validator in self.pre_validators:
                try:
                    validator(self.data_processed, self._form, self)
                except ValidationError as error:
                    self.append_error(error.message)
        except StopValidation as error:
            self.append_error(error.message)
            self.validation_stopped = True
        except ClearValidation:
            self._errors = {}
            self.validation_stopped = False

    def validate(self) -> bool:
        """
        the primary validator which runs default validators of the field and additional validators given by the form
        definition
        """
        if self.validation_stopped is True:
            self.state = FieldState.validated
            return not self.has_errors
        if self.data_processed is unset_value and self.required:
            self.append_error('data required')
            self.validation_stopped = True
            return not self.has_errors
        if self.data_processed is unset_value and not self.required:
            self.state = FieldState.validated
            return not self.has_errors
        try:
            for validator in self.default_validators + self.validators:
                try:
                    validator(self.data, self._form, self)
                except ValidationError as error:
                    self.append_error(error.message)
        except StopValidation as error:
            self.append_error(error.message)
        except ClearValidation:
            self._errors = {}
        self.state = FieldState.validated
        return not self.has_errors

    def append_error(self, error: str):
        if self._field_name not in self._errors:
            self._errors[self._field_name] = []
        self._errors[self._field_name].append(error)

    @property
    def errors(self) -> dict:
        """
        errors are always flat dictionaries. nested errors are separated by dots like
        bakery.cookies.1.flavor = 'chocolate'
        """
        return self._errors

    @property
    def has_errors(self) -> bool:
        return len(self._errors) > 0

    @property
    def data(self):
        """
        data is the primary interface to anything from outside wanting to access data of fields
        """
        return self.data_processed

    @property
    def out(self):
        """
        out is quite the same as data, but after output filters and without custom objects in case of dicts.
        """
        if self.data_out is not unset_value or self.data is unset_value:
            return self.data_out
        self.data_out = self.data
        for output_filter in self.default_input_filters + self.output_filters:
            self.data_out = output_filter(self.data_out)
        return self.data_out
