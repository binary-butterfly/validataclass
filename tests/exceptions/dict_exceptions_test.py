# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import DictFieldsValidationError, DictRequiredFieldError, InvalidTypeError


class DictFieldsValidationErrorTest:
    """
    Tests for the DictFieldsValidationError exception class.
    """

    @staticmethod
    def test_dict_field_errors():
        """ Tests DictFieldsValidationError with field validation errors. """
        error = DictFieldsValidationError(field_errors={
            'missing_field': DictRequiredFieldError(),
            'invalid_type_field': InvalidTypeError(expected_types=int),
        })

        assert repr(error) == "DictFieldsValidationError(code='field_errors', field_errors={" + \
               "'missing_field': DictRequiredFieldError(code='required_field'), " + \
               "'invalid_type_field': InvalidTypeError(code='invalid_type', expected_type='int')})"
        assert str(error) == repr(error)
        assert error.to_dict() == {
            'code': 'field_errors',
            'field_errors': {
                'missing_field': {'code': 'required_field'},
                'invalid_type_field': {'code': 'invalid_type', 'expected_type': 'int'},
            },
        }
