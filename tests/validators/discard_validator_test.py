"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, List

import pytest

from validataclass.helpers import UnsetValue
from validataclass.validators import DiscardValidator


class DiscardValidatorTest:
    """
    Unit tests for the DiscardValidator.
    """

    example_input_data: List[Any] = [
        None,
        True,
        False,
        'banana',
        42,
        [],
        {},
    ]

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        example_input_data,
    )
    def test_discard_and_return_none(input_data):
        """ Test that DiscardValidator accepts anything and always returns None by default. """
        validator = DiscardValidator()
        assert validator.validate(input_data) is None

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        example_input_data,
    )
    @pytest.mark.parametrize(
        'output_value',
        [
            None,
            True,
            'discarded value',
            UnsetValue,
        ],
    )
    def test_discard_and_return_custom_value(input_data, output_value):
        """ Test that DiscardValidator always returns the output_value parameter if it is set. """
        validator = DiscardValidator(output_value=output_value)
        result = validator.validate(input_data)

        assert type(result) is type(output_value)
        assert result == output_value

    @staticmethod
    def test_output_value_is_deepcopied():
        """
        Test that the given output value is deepcopied, e.g. always return a different instance of an empty list with
        `output_value=[]`.
        """
        validator = DiscardValidator(output_value=[42])
        first_list = validator.validate('banana')
        second_list = validator.validate('banana')

        assert first_list == [42]
        assert second_list == [42]
        assert first_list is not second_list
