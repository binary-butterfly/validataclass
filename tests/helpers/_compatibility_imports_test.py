"""
validataclass
Copyright (c) 2022, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import pytest


class HelpersCompatibilityImportsTest:
    """ Tests backwards compatibility imports from validataclass.helpers. """

    @staticmethod
    def test_import_from_dataclasses():
        """ Tests deprecated imports from the compatibility module validataclass.helpers.dataclasses. """
        with pytest.deprecated_call():
            from validataclass.helpers.dataclasses import validataclass, validataclass_field
            assert callable(validataclass)
            assert callable(validataclass_field)

    @staticmethod
    def test_import_from_dataclass_defaults():
        """ Tests deprecated imports from the compatibility module validataclass.helpers.dataclass_defaults. """
        with pytest.deprecated_call():
            from validataclass.helpers.dataclass_defaults import Default, DefaultFactory, DefaultUnset, NoDefault
            assert type(Default) is type
            assert issubclass(DefaultFactory, Default)
            assert isinstance(DefaultUnset, Default)
            assert isinstance(NoDefault, Default)

    @staticmethod
    def test_import_from_dataclass_mixins():
        """ Tests deprecated imports from the compatibility module validataclass.helpers.dataclass_mixins. """
        with pytest.deprecated_call():
            from validataclass.helpers.dataclass_mixins import ValidataclassMixin
            assert type(ValidataclassMixin) is type

    @staticmethod
    def test_import_from_helpers_package():
        """ Tests deprecated imports from the validataclass.helpers package. """
        with pytest.deprecated_call():
            from validataclass.helpers import (
                Default, DefaultFactory, DefaultUnset, NoDefault,  # noqa (not declared in __all__)
                validataclass, validataclass_field, ValidataclassMixin,  # noqa (not declared in __all__)
            )

            assert type(Default) is type
            assert issubclass(DefaultFactory, Default)
            assert isinstance(DefaultUnset, Default)
            assert isinstance(NoDefault, Default)
            assert callable(validataclass)
            assert callable(validataclass_field)
            assert type(ValidataclassMixin) is type

    @staticmethod
    def test_import_from_helpers_package_fallback_to_exception():
        """ Tests __getattr__ raises an AttributeError for unknown imports. """
        with pytest.raises(ImportError, match="cannot import name 'Foobar' from 'validataclass.helpers'"):
            from validataclass.helpers import Foobar  # noqa (unused import; not declared in __all__)
