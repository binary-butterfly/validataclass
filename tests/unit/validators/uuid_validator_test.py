import pytest

from validataclass.exceptions import RequiredValueError, InvalidTypeError
from validataclass.exceptions.uuid_exceptions import InvalidUUIDError
from validataclass.validators.uuid_validator import UUIDValidator


class UUIDValidatorTest:
    """
    Unit tests for the UUIDValidator.
    """

    # General tests

    @staticmethod
    def test_invalid_none():
        """ Check that UUIDValidator raises exceptions for None as value. """
        validator = UUIDValidator()

        with pytest.raises(RequiredValueError) as exception_info:
            validator.validate(None)

        assert exception_info.value.to_dict() == {'code': 'required_value'}

    @staticmethod
    def test_invalid_wrong_type():
        """ Check that UUIDValidator raises exceptions for values that are not of type 'str'. """
        validator = UUIDValidator()

        with pytest.raises(InvalidTypeError) as exception_info:
            validator.validate(123)

        assert exception_info.value.to_dict() == {
            'code': 'invalid_type',
            'expected_type': 'str',
        }

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            '',
            'unit test apple',
        ],
    )
    def test_invalid_string(input_data):
        """ Test UUIDValidator with invalid strings. """
        validator = UUIDValidator()

        with pytest.raises(InvalidUUIDError) as exception_info:
            validator.validate(input_data)

        assert exception_info.value.to_dict() == {'code': 'invalid_uuid'}

    @staticmethod
    @pytest.mark.parametrize(
        'input_data',
        [
            # Nil UUID
            # https://www.rfc-editor.org/info/rfc9562/#section-5.9
            "00000000-0000-0000-0000-000000000000",
            # UUID Version 1
            # https://www.rfc-editor.org/info/rfc9562/#section-5.1
            'eb720958-dc2f-11f1-affb-426ea6d26eca',
            # UUID Version 3
            # https://www.rfc-editor.org/info/rfc9562/#section-5.3
            '397792c4-039c-3d7d-ab8d-f79803300084',
            # UUID Version 4
            # https://www.rfc-editor.org/info/rfc9562/#section-5.4
            '77736bec-8d9d-4c7d-b1e4-5f90f4c19b25',
            # UUID Version 5
            # https://www.rfc-editor.org/info/rfc9562/#section-5.5
            '6423fa3e-a882-51db-9091-95d0ded7c88d',
        ],
    )
    def test_valid_string(input_data):
        """ Test UUIDValidator with valid strings. """
        validator = UUIDValidator()
        assert str(validator.validate(input_data)) == input_data
