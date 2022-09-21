"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

import pytest

from validataclass.validators import Validator


class ValidatorTest:
    """
    Unit tests for the Validator base class.
    """

    @staticmethod
    def test_validate_without_kwargs_deprecation():
        """ Test that creating a Validator subclass that does not accept context arguments raises a deprecration warning. """
        # Ensure that Validator creation causes a DeprecationWarning
        with pytest.deprecated_call():
            class ValidatorWithoutKwargs(Validator):
                def validate(self, input_data: Any) -> Any:  # noqa (missing parameter)
                    return input_data

        # Check that validate_with_context() calls validate() without errors
        validator = ValidatorWithoutKwargs()
        assert validator.validate_with_context('banana', foo=42, bar=13) == 'banana'
