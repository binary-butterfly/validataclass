"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from mypy.options import Options
from mypy.plugin import ClassDefContext, FunctionContext, Plugin, ReportConfigContext
from mypy.plugins.dataclasses import dataclass_tag_callback
from mypy.types import Type
from typing_extensions import override

from .constants import VALIDATACLASS_DECORATORS, VIRTUAL_FIELD_WRAPPER_FUNC
from .debug_logger import DebugLogger
from .field_type_resolver import FieldTypeResolver
from .parsed_field_cache import ParsedFieldCache
from .plugin_config import PluginConfig, PluginConfigParser, PluginConfigParseError
from .validataclass_transformer import ValidataclassTransformer


def _load_plugin_config(config_file: str | None) -> PluginConfig:
    """
    Load configuration for the validataclass mypy plugin from the mypy configuration, i.e. the same config file
    that mypy is currently using.

    If there is an error parsing the config, print that error message and exit with a non-zero exit code
    """
    # Fallback to empty config if there is no mypy config
    if config_file is None:  # pragma: nocover
        return PluginConfig()

    config_parser = PluginConfigParser()
    try:
        return config_parser.load_config(Path(config_file))
    except PluginConfigParseError as exc:  # pragma: nocover
        print(f'Error while parsing plugin config for validataclass mypy plugin:\n{exc}')
        exit(1)


class ValidataclassPlugin(Plugin):
    """
    Custom mypy plugin for validataclass support.
    """

    # Plugin config
    _plugin_config: PluginConfig

    # Logger class for easier debugging
    _logger: DebugLogger

    # Internal cache for parsed validataclass fields, shared between all instances of FieldTypeResolver
    _parsed_field_cache: ParsedFieldCache

    # Set of all validataclass decorators, including the built-in ones and user-defined ones from the plugin config
    _validataclass_decorator_fullnames: set[str]

    def __init__(self, options: Options):
        super().__init__(options)

        # Load plugin config
        self._plugin_config = _load_plugin_config(options.config_file)

        # Initialize dependencies
        self._logger = DebugLogger(debug_mode=self._plugin_config.debug_mode)
        self._parsed_field_cache = ParsedFieldCache()

        # Cache some values for easier access
        self._validataclass_decorator_fullnames = (
            VALIDATACLASS_DECORATORS | self._plugin_config.custom_validataclass_decorators
        )

    @override
    def report_config_data(self, ctx: ReportConfigContext) -> Any:
        """
        Get representation of configuration data for a module.

        This hook is called once or twice for every module (i.e. Python file): Once after loading the metadata cache to
        check if the cache for this module needs to be invalidated, and if yes, another time at the end to write new
        cache information.

        It's intended for custom plugin configuration, so that mypy rechecks cached files if the plugin config has been
        changed.

        We misuse this hook a little bit here to work around the limitations of mypy's caching system. With the current
        approach, we need to parse every validataclass in every run and cannot rely on the mypy cache. This means we
        need to invalidate the cache for every module that defines a validataclass. Since all these classes depend on
        the `@validataclass` decorator, it's enough to invalidate the cache for the module that defines this decorator,
        all dependent files will automatically be rechecked. To force cache invalidation, we can just return the current
        timestamp here.

        TODO: This is a workaround that partially disables caching (which is still better than disabling caching
          completely). We should find a better solution that works without cache invalidation, but for now this is fine.
        """
        # Always invalidate cache for the module that defines the validataclass decorator to trigger rechecking of all
        # files that define validataclasses.
        if ctx.id == 'validataclass.dataclasses.validataclass':
            return str(datetime.now())

        return None

    @override
    def get_class_decorator_hook(self, fullname: str) -> Callable[[ClassDefContext], None] | None:
        """
        Update class definition of classes decorated with the given decorator (here, the `@validataclass` decorator).

        (For details, see docs for `mypy.plugin.Plugin`.)

        In this plugin, we use this hook to tag all validataclasses so that we can recognize them later.
        We also call the corresponding callback of the dataclass plugin because it wouldn't be called otherwise.
        """
        # Tag all classes decorated with `@validataclass` or a similar decorator for later.
        if fullname in self._validataclass_decorator_fullnames:
            return self._validataclass_decorator_tag_callback

        return None

    @override
    def get_class_decorator_hook_2(self, fullname: str) -> Callable[[ClassDefContext], bool] | None:
        """
        Update class definition of classes decorated with the given decorator (here, the `@validataclass` decorator).

        Similar to `get_class_decorator_hook`, but this runs in a later pass when placeholders have been resolved.
        The hook can return False if some base class hasn't been processed yet, in which case the hook will be called
        another time later.

        (For details, see docs for `mypy.plugin.Plugin`.)

        In this plugin, we transform the definition of validataclasses by wrapping each field definition (e.g. tuples of
        validator and default) in a virtual wrapper function which is analyzed later in `get_function_hook`.
        """
        # Update classes decorated with `@validataclass` or a similar decorator.
        if fullname in self._validataclass_decorator_fullnames:
            return self._validataclass_decorator_transform_callback

        return None

    @override
    def get_function_hook(self, fullname: str) -> Callable[[FunctionContext], Type] | None:
        """
        Adjust the return type of a function call.

        (For details, see docs for `mypy.plugin.Plugin`.)

        In this plugin, we use this hook to analyze validataclass field definitions that have been wrapped in a virtual
        wrapper function during `get_class_decorator_hook_2`. We check the field definition for validators and default
        objects and adjust the return type to be the combined type of validator output and default value.

        For example, given a validataclass with the following field definition:

            example: str | None = StringValidator(), Default(None)

        The right-hand side of this assignment would be wrapped in a virtual function call ("virtual" meaning it only
        exists for the type checker) by the class decorator hook, changing the field to something similar to:

            example: str | None = _virtual_field_wrapper((StringValidator(), Default(None)), [additional metadata])

        In the function hook, we can now analyze the wrapped expression (in this case a tuple) and find the validator
        and default object. Then we evaluate their types (e.g. the StringValidator returns `str`, the default has a
        value of `None`) and adjust the return type of the virtual wrapper function to the actual type that this field
        can have according to its validator and default. In the example, the return type is changed to `str | None`.

        Now if the return type doesn't match the field annotation on the left-hand side, mypy can report a proper error.
        """
        # Adjust return type of all calls to the virtual field wrapper function.
        if fullname == VIRTUAL_FIELD_WRAPPER_FUNC:
            return self._virtual_field_wrapper_callback

        return None

    @staticmethod
    def _validataclass_decorator_tag_callback(ctx: ClassDefContext) -> None:
        """
        Callback for the class decorator hook for classes decorated with `@validataclass`.

        Tag all `@validataclass`-decorated classes both as a validataclass and a regular dataclass.
        """
        # Tag class so we can recognize it as a validataclass later (the value of the tag is ignored)
        ctx.cls.info.metadata["validataclass_tag"] = {}

        # Default dataclass plugin: Tag class as a dataclass
        dataclass_tag_callback(ctx)

    def _validataclass_decorator_transform_callback(self, ctx: ClassDefContext) -> bool:
        """
        Callback for the second-pass class decorator hook for classes decorated with `@validataclass`.

        Transform all `@validataclass`-decorated classes for later analysis.
        """
        transformer = ValidataclassTransformer(
            ctx=ctx,
            logger=self._logger,
        )
        return transformer.transform()

    def _virtual_field_wrapper_callback(self, ctx: FunctionContext) -> Type:
        """
        Callback for the function hook for the virtual wrapper function.

        Analyze type of field definition and adjust function return type.
        """
        resolver = FieldTypeResolver(
            ctx=ctx,
            plugin_config=self._plugin_config,
            logger=self._logger,
            parsed_field_cache=self._parsed_field_cache,
        )
        return resolver.resolve()


# This function is expected by mypy to load the plugin
def plugin(_version: str) -> type[ValidataclassPlugin]:
    # Ignore version argument if the plugin works with all mypy versions
    return ValidataclassPlugin
