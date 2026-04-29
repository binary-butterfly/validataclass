"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from validataclass.exceptions import DictInvalidKeyTypeError, InvalidTypeError, RequiredValueError
from validataclass.validators import AnyDictValidator


class AnyDictValidatorTest:
    """
    Unit tests for the AnyDictValidator.
    """

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            # Empty dictionary
            {},

            # Regular dictionary with different value types, also empty string as key (not forbidden)
            {'foo': 42, 'bar': 'meow', 'baz': None, '': 'empty key'},

            # Nested dictionaries, which *can* have non-string keys because they are not supposed to be validated
            {'foo': {'a': 42, 'b': 'c'}, 'bar': {1: 42, 2: 'foo'}, 'baz': {}},
        ],
    )
    def test_valid_dicts(input_data):
        """ Test AnyDictValidator with valid input dictionaries. """
        validator = AnyDictValidator()

        # Validation should always return the unmodified input dictionary (if valid)
        assert validator.validate(input_data) == input_data

    @staticmethod
    def test_invalid_none():
        """ Check that AnyDictValidator raises exceptions for None as value. """
        validator = AnyDictValidator()

        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)

        assert exception_info.value.to_dict() == {
            'code': 'required_value',
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            True,
            False,
            42,
            'banana',
            [],
            ['list'],
            [{'list': 'of dicts'}],
        ],
    )
    def test_invalid_wrong_type(input_data):
        """ Check that AnyDictValidator raises exceptions for values that are not of type `dict`. """
        validator = AnyDictValidator()

        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(input_data)

        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'dict',
        }

    @staticmethod
    def test_invalid_key_types():
        """ Check that AnyDictValidator raises exceptions for dictionaries with non-string keys. """
        validator = AnyDictValidator()

        with pytest.raises(DictInvalidKeyTypeError) as exception_info:
            validator.validate({42: 'foo'})

        assert exception_info.value.to_dict() == {
            'code': 'dict_invalid_key_type',
        }
