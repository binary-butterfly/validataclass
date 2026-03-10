"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import os
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: nocover
    import tomli as tomllib


# TODO: Add unit tests for config parsing and error handling (and remove "pragma: nocover"s).

class PluginConfig:
    """
    Plugin configuration for the validataclass mypy plugin.
    """

    # Whether debug mode is enabled, which results in a lot of debug log messages.
    # Can also be set via environment variable VALIDATACLASS_MYPY_DEBUG.
    debug_mode: bool

    # Custom decorators that turn a class into a validataclass (see also .constants.VALIDATACLASS_DECORATORS)
    custom_validataclass_decorators: set[str]

    # Custom functions that create validataclass fields, must have a signature compatible to validataclass_field()
    custom_field_functions: set[str]

    # Custom types of objects that are allowed (read: ignored) in a field definition. This can be used in combination
    # with the custom decorators to allow additional options in a field.
    ignore_custom_types_in_fields: set[str]

    def __init__(
        self,
        *,
        debug_mode: bool = False,
        custom_validataclass_decorators: set[str] | list[str] | None = None,
        custom_field_functions: set[str] | list[str] | None = None,
        ignore_custom_types_in_fields: set[str] | list[str] | None = None,
    ):
        self.debug_mode = debug_mode
        self.custom_validataclass_decorators = set(custom_validataclass_decorators or [])
        self.custom_field_functions = set(custom_field_functions or [])
        self.ignore_custom_types_in_fields = set(ignore_custom_types_in_fields or [])


class PluginConfigParseError(Exception):
    """
    Exception raised when there is an error while parsing the plugin config.
    """


class PluginConfigParser:
    """
    Parser for plugin config.
    """

    def load_config(self, config_file: Path) -> PluginConfig:
        """
        Load plugin configuration for the validataclass mypy plugin from a file (currently, only pyproject.toml files
        are supported).
        """
        # Currently only pyproject.toml format is supported to configure the validataclass mypy plugin
        if not config_file.suffix.lower() == '.toml':  # pragma: nocover
            # Return default config
            return PluginConfig()

        parsed_config = self._parse_pyproject_toml(config_file)

        # Allow overriding some settings via environment variables (for now, only debug mode)
        if (env_debug := os.getenv('VALIDATACLASS_MYPY_DEBUG', None)) is not None:  # pragma: nocover
            parsed_config.debug_mode = bool(env_debug)

        return parsed_config

    def _parse_pyproject_toml(self, config_file: Path) -> PluginConfig:
        """
        Parse a TOML file in the style of pyproject.toml with the given filename.
        """
        try:
            # Load TOML file into dictionary
            with config_file.open('rb') as toml_file:
                toml_data = tomllib.load(toml_file)
        except tomllib.TOMLDecodeError as exc:  # pragma: nocover
            raise PluginConfigParseError(f'{config_file}: {exc}') from exc

        # Check for [tool.validataclass_mypy] section.
        # For tests, we also need to support [tool.mypy.x_validataclass] as an alternative, due to this line:
        # https://github.com/typeddjango/pytest-mypy-plugins/blob/3.3.0/pytest_mypy_plugins/configs.py#L57
        tool_sections = toml_data.get('tool', {})
        if 'validataclass_mypy' in tool_sections:  # pragma: nocover
            config_section = 'tool.validataclass_mypy'
            raw_config = tool_sections['validataclass_mypy']
        elif 'x_validataclass' in tool_sections.get('mypy', {}):
            config_section = 'tool.mypy.x_validataclass'
            raw_config = tool_sections['mypy']['x_validataclass']
        else:
            return PluginConfig()

        try:
            # Parse raw config
            return self._parse_raw_config(raw_config)
        except (ValueError, TypeError) as exc:  # pragma: nocover
            raise PluginConfigParseError(f'{config_file}: [{config_section}]: {exc}') from exc

    def _parse_raw_config(self, raw_config: dict[str, Any]) -> PluginConfig:
        """
        Parse the content of the `[tool.validataclass_mypy]` section of a pyproject.toml file.
        """
        return PluginConfig(
            debug_mode=self._parse_as_bool(raw_config, 'debug_mode', False),
            custom_validataclass_decorators=self._parse_as_str_list(raw_config, 'custom_validataclass_decorators'),
            custom_field_functions=self._parse_as_str_list(raw_config, 'custom_field_functions'),
            ignore_custom_types_in_fields=self._parse_as_str_list(raw_config, 'ignore_custom_types_in_fields'),
        )

    @staticmethod
    def _parse_as_bool(raw_config: dict[str, Any], key: str, default: bool) -> bool:
        """
        Retrieve the value with the given key from the raw config dictionary, parse it as a boolean and raise an
        exception if it's invalid.
        """
        raw = raw_config.get(key, default)
        if not isinstance(raw, bool):  # pragma: nocover
            raise TypeError(f'{key}: Must be a boolean')
        return raw

    @staticmethod
    def _parse_as_str_list(raw_config: dict[str, Any], key: str) -> list[str]:
        """
        Retrieve the value with the given key from the raw config dictionary, parse it as a list of strings and raise
        an exception if it's invalid.
        """
        raw = raw_config.get(key, [])
        if not isinstance(raw, list) or any(not isinstance(item, str) for item in raw):  # pragma: nocover
            raise TypeError(f'{key}: Must be a list of strings')
        return raw
