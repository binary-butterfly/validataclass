"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest

from tests.test_utils import UNSET_PARAMETER
from validataclass.exceptions import RequiredValueError, InvalidTypeError, InvalidValidatorOptionException
from validataclass.validators import AnythingValidator


class AnythingValidatorTest:
    """
    Unit tests for the AnythingValidator.
    """

    # Tests with and without allow_none

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            # Various scalar data (except None, which is tested separately)
            True,
            False,
            'banana',
            1312,

            # Lists and dictionaries
            [],
            ['foobar', 42],
            {},
            {'foo': 'banana', 'bar': 42},
        ]
    )
    @pytest.mark.parametrize('allow_none', [UNSET_PARAMETER, True, False])
    def test_accept_anything_except_none(input_data, allow_none):
        """ Test that AnythingValidator accepts anything that is not None regardless of the allow_none parameter. """
        validator = AnythingValidator() if allow_none is UNSET_PARAMETER \
            else AnythingValidator(allow_none=allow_none)

        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize('allow_none', [UNSET_PARAMETER, True])
    def test_accept_none(allow_none):
        """ Test that AnythingValidator accepts None by default (no allow_none parameter) and when allow_none=True. """
        validator = AnythingValidator() if allow_none is UNSET_PARAMETER \
            else AnythingValidator(allow_none=allow_none)

        assert validator.validate(None) is None

    @staticmethod
    def test_reject_none():
        """ Test that AnythingValidator rejects None when allow_none=False. """
        validator = AnythingValidator(allow_none=False)

        with pytest.raises(RequiredValueError) as exc_info:
            validator.validate(None)
        assert exc_info.value.to_dict() == {'code': 'required_value'}

    # Tests with allowed_types (and allow_none)

    @staticmethod
    @pytest.mark.parametrize(
        'allow_none, allowed_types, input_data',
        [
            # Single type (should be automatically converted to list)
            (UNSET_PARAMETER, int, 42),

            # Single type (allow None)
            (True, int, 42),
            (True, int, None),

            # List with one type (explicitly no None)
            (False, [str], ''),
            (False, [str], 'banana'),

            # Set with multiple types (implicitly no None)
            (UNSET_PARAMETER, {str, int}, 'banana'),
            (UNSET_PARAMETER, {str, int}, 42),

            # Set with multiple types (additionally allow none)
            (True, {str, int}, 'banana'),
            (True, {str, int}, 42),
            (True, {str, int}, None),

            # List that contains None (should be automatically converted to NoneType)
            (UNSET_PARAMETER, [int, None], 42),
            (UNSET_PARAMETER, [int, None], None),

            # List that contains NoneType (auto-determine allow_none)
            (UNSET_PARAMETER, [int, type(None)], 42),
            (UNSET_PARAMETER, [int, type(None)], None),

            # List that contains NoneType (explicitly with allow_none=True)
            (True, [int, type(None)], 42),
            (True, [int, type(None)], None),

            # List that contains NoneType, but explicitly REMOVING NoneType with allow_none=False
            (False, [int, type(None)], 42),
        ]
    )
    def test_allowed_types_valid(allow_none, allowed_types, input_data):
        """ Test AnythingValidator with allowed_types and/or allow_none parameters with valid input. """
        allow_none_args = {'allow_none': allow_none} if allow_none is not UNSET_PARAMETER else {}
        validator = AnythingValidator(**allow_none_args, allowed_types=allowed_types)

        assert validator.validate(input_data) == input_data

    @staticmethod
    @pytest.mark.parametrize(
        'allow_none, allowed_types, input_data, error_expected_types',
        [
            # NOTE: Tests where None is an invalid value need to be tested in a separate test (below) since the error
            # looks different there (RequiredValueError instead of InvalidTypeError)

            # Single type (implicitly no None)
            (UNSET_PARAMETER, int, True, 'int'),
            (UNSET_PARAMETER, int, 0.42, 'int'),
            (UNSET_PARAMETER, int, 'banana', 'int'),

            # Single type (allow None)
            (True, int, True, ['int', 'none']),
            (True, int, 'banana', ['int', 'none']),

            # List with one type (explicitly no None)
            (False, [str], 123, 'str'),
            (False, [str], ['foo'], 'str'),

            # Set with multiple types (implicitly no None)
            (UNSET_PARAMETER, {str, int}, True, ['int', 'str']),
            (UNSET_PARAMETER, {str, int}, 0.123, ['int', 'str']),
            (UNSET_PARAMETER, {str, int}, [42], ['int', 'str']),

            # Set with multiple types (additionally allow none)
            (True, {str, int}, True, ['int', 'none', 'str']),
            (True, {str, int}, 0.123, ['int', 'none', 'str']),

            # List that contains None (should be automatically converted to NoneType)
            (UNSET_PARAMETER, [int, None], 0.123, ['int', 'none']),

            # List that contains NoneType (auto-determine allow_none)
            (UNSET_PARAMETER, [int, type(None)], 'banana', ['int', 'none']),

            # List that contains NoneType (explicitly with allow_none=True)
            (True, [int, type(None)], 'banana', ['int', 'none']),

            # List that contains NoneType, but explicitly REMOVING NoneType with allow_none=False
            (False, [int, type(None)], 'banana', 'int'),
        ]
    )
    def test_allowed_types_invalid(allow_none, allowed_types, input_data, error_expected_types):
        """ Test AnythingValidator with allowed_types and/or allow_none parameters with invalid input. """
        allow_none_args = {'allow_none': allow_none} if allow_none is not UNSET_PARAMETER else {}
        validator = AnythingValidator(**allow_none_args, allowed_types=allowed_types)

        with pytest.raises(InvalidTypeError) as exc_info:
            validator.validate(input_data)

        assert exc_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_types' if type(error_expected_types) is list else 'expected_type': error_expected_types,
        }

    @staticmethod
    @pytest.mark.parametrize(
        'allow_none, allowed_types',
        [
            # allowed_types without NoneType, without setting allow_none
            (UNSET_PARAMETER, int),
            (UNSET_PARAMETER, [str]),
            (UNSET_PARAMETER, {str, int}),

            # allowed_types without NoneType, explicitly setting allow_none=False
            (False, int),
            (False, [str]),
            (False, {str, int}),

            # allowed_types contains NoneType, but is explicitly REMOVED with allow_none=False
            (False, [int, type(None)]),
        ]
    )
    def test_allowed_types_invalid_none(allow_none, allowed_types):
        """ Test AnythingValidator with allowed_types and/or allow_none parameters with None as invalid input. """
        allow_none_args = {'allow_none': allow_none} if allow_none is not UNSET_PARAMETER else {}
        validator = AnythingValidator(**allow_none_args, allowed_types=allowed_types)

        with pytest.raises(RequiredValueError) as exc_info:
            validator.validate(None)
        assert exc_info.value.to_dict() == {'code': 'required_value'}

    # Invalid parameter tests

    @staticmethod
    @pytest.mark.parametrize(
        'allowed_types, error_type_repr',
        [
            # Single object that is not a type
            ('banana', "'banana'"),

            # Lists/sets that contain something that is not a type
            (['banana'], "'banana'"),
            ([int, [str]], "[<class 'str'>]"),
            ({int, str, 42}, '42'),
        ]
    )
    def test_invalid_allowed_types(allowed_types, error_type_repr):
        """ Test that AnythingValidator raises an error on construction if allowed_types contains something that is not a type. """
        with pytest.raises(InvalidValidatorOptionException) as exc_info:
            AnythingValidator(allowed_types=allowed_types)
        assert str(exc_info.value) == f'Element of allowed_types is not a type: {error_type_repr}'

    @staticmethod
    def test_empty_allowed_types():
        """ Test that AnythingValidator raises an error on construction if allowed_types is empty. """
        with pytest.raises(InvalidValidatorOptionException) as exc_info:
            AnythingValidator(allowed_types=[])
        assert str(exc_info.value) == 'allowed_types is empty. Use the RejectValidator instead.'
