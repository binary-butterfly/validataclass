# encoding: utf-8

"""
binary butterfly validator
Copyright (c) 2021, binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from wtfjson.exceptions import ListItemsValidationError, InvalidTypeError, NumberRangeError


class ListItemsValidationErrorTest:
    """
    Tests for the ListItemsValidationError exception class.
    """

    @staticmethod
    def test_list_item_errors():
        """ Tests ListItemsValidationError with list item validation errors. """
        error = ListItemsValidationError(item_errors={
            1: InvalidTypeError(expected_types=int),
            3: NumberRangeError(min_value=1),
        })

        assert repr(error) == "ListItemsValidationError(code='list_item_errors', item_errors={" + \
               "1: InvalidTypeError(code='invalid_type', expected_type='int'), " + \
               "3: NumberRangeError(code='number_range_error', min_value=1)})"
        assert str(error) == repr(error)
        assert error.to_dict() == {
            'code': 'list_item_errors',
            'item_errors': {
                1: {'code': 'invalid_type', 'expected_type': 'int'},
                3: {'code': 'number_range_error', 'min_value': 1},
            },
        }
