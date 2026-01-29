"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any

from mypy.errorcodes import ErrorCode
from mypy.nodes import (
    Argument,
    ArgKind,
    AssignmentStmt,
    CallExpr,
    ClassDef,
    Context,
    Expression,
    FuncDef,
    GDEF,
    NameExpr,
    TempNode,
    Var,
)
from mypy.plugin import ClassDefContext, SemanticAnalyzerPluginInterface
from mypy.plugins.dataclasses import dataclass_class_maker_callback, DATACLASS_FIELD_SPECIFIERS
from mypy.types import AnyType, CallableType, TypeOfAny, UnboundType

from .constants import (
    ERROR_CODE_VALIDATACLASS,
    VALIDATACLASS_FIELD_FUNC,
    VIRTUAL_FIELD_WRAPPER_FUNC,
    VIRTUAL_FIELD_WRAPPER_FUNC_NAME,
)
from .helpers import DebugLogger


class ValidataclassTransformer:
    """
    Handler for class decorator hook to transform a `@validataclass`-decorated class for type checking.

    Ensures that the default dataclass plugin callbacks are called as well if necessary.
    """

    _ctx: ClassDefContext

    # Class definition that is being transformed
    _class_def: ClassDef

    # The decorator expression that's applied to the class
    _decorator: Expression

    # Interface to mypy's semantic analyzer
    _api: SemanticAnalyzerPluginInterface

    # Logger for plugin development and debugging
    _logger: DebugLogger

    def __init__(self, ctx: ClassDefContext, logger: DebugLogger):
        self._ctx = ctx
        self._class_def = ctx.cls
        self._decorator = ctx.reason
        self._api = ctx.api
        self._logger = logger

    def _get_logger_context(self, context: Context | None) -> str:
        """
        Returns a string representation of the given context, i.e. the full class name and line number.
        """
        if context is None:
            context = self._decorator
        return f'{self._class_def.fullname}:{context.line}'

    def _log_warn(self, context: Context | None, msg: str, *objects: Any) -> None:
        """
        Logs a message on WARN level.
        Use this to warn about unhandled expressions/types or features that are not implemented yet.
        """
        return self._logger.log('WARN', self._get_logger_context(context), msg, *objects)

    def _log_debug(self, context: Context | None, msg: str, *objects: Any) -> None:
        """
        Logs a message on DEBUG level. Only printed if debug mode is enabled.
        Use this for better traceability and debugging of what the plugin is doing.
        """
        return self._logger.log('DEBUG', self._get_logger_context(context), msg, *objects)

    def _fail(self, msg: str, context: Context, *, code: ErrorCode | None = None) -> None:
        """
        Reports a mypy error to the user. Default code is "validataclass".
        """
        self._api.fail(msg, context, code=code or ERROR_CODE_VALIDATACLASS)

    def transform(self) -> bool:
        """
        Update the class definition of a validataclass by wrapping the right-hand side of field definitions in the
        virtual field wrapper function, so that the types can be analyzed later in the function hook.

        Additionally take care of running the hooks of the mypy dataclass plugin, which generates the definitions of
        special functions like `__init__`, and modify these definitions if necessary.

        Called for every class that is decorated with `@validataclass` (or an equivalent decorator).
        """
        self._log_debug(None, 'Analyzing decorated validataclass')

        # TODO: Parse base classes in reverse MRO and collect fields defined in these base classes.
        # TODO: Make sure all base classes have been processed already.
        self._log_debug(None, 'Base classes', self._class_def.info.bases)
        bases = [str(base) for base in self._class_def.info.bases]
        if bases != ['builtins.object']:
            self._log_warn(None, 'validataclass with base classes, not implemented yet', bases)

        # Iterate over all statements of the class body
        for stmt in self._class_def.defs.body:
            # There are a lot of different types of statements that we could theoretically encounter here. Most of them
            # are either irrelevant for us here (e.g. method definitions) or because they don't make sense within a
            # validataclass definition (e.g. loops, conditionals, throw/return statements, ...).
            # For now we are only interested in assignment statements like `field: type = SomeValidator()`.
            if not isinstance(stmt, AssignmentStmt):
                self._log_debug(stmt, f'Skipping statement of type {type(stmt)}')
                continue

            # There are more edge cases for the left-hand side that we can skip for now, like multiple assignments
            # (`x, y = z`) or chained assignments (`x = y = z`).
            # TODO: Check if there are edge cases that we should handle, or that we should even report an error for!
            lvalue = stmt.lvalues[0] if len(stmt.lvalues) == 1 else None
            if lvalue is None or not isinstance(lvalue, NameExpr):
                self._log_warn(stmt, 'Skipping weird edge case for assignment LHS', stmt.lvalues)
                continue

            # Edge case for right-hand side: We can have a type annotation statement without an assignment (`x: int`),
            # which mypy represents as an AssignmentStmt with a TempNode(AnyType, no_rhs=True) as rvalue
            # TODO: This isn't allowed in validataclasses, we should report an error for this
            if isinstance(stmt.rvalue, TempNode) and stmt.rvalue.no_rhs:
                self._log_warn(stmt, f'Skipping assignment for "{lvalue.name}" without RHS')
                continue

            # The validataclass decorator ignores attributes without annotations and those that start with a '_'.
            if stmt.type is None:
                self._log_debug(stmt, f'Skipping assignment for "{lvalue.name}" without type annotation')
                continue
            if lvalue.name.startswith('_'):
                self._log_debug(stmt, f'Skipping assignment for "{lvalue.name}" because it starts with an underscore')
                continue

            # Skip fields that are already wrapped or created with field specifier functions
            if isinstance(stmt.rvalue, CallExpr) and isinstance(stmt.rvalue.callee, NameExpr):
                callee_name = stmt.rvalue.callee.fullname

                # Ignore fields that have been created with the regular dataclasses.field() or similar
                if callee_name in DATACLASS_FIELD_SPECIFIERS:
                    self._log_debug(stmt, f'Skipping field "{lvalue.name}" with {callee_name}')
                    continue

                # Skip fields that have been created with validataclass_field()
                # TODO: I think we need to wrap these too actually :/
                if callee_name == VALIDATACLASS_FIELD_FUNC:
                    # TODO: Normalize `default` - if it's NoDefault, remove the default instead?
                    # TODO: (Can probably be ignored because we'll have to fix __init__ manually anyway.)
                    self._log_debug(stmt, f'Skipping field "{lvalue.name}" with validataclass_field()')
                    continue

                # Skip field if it has already been wrapped in a previous pass
                if callee_name == VIRTUAL_FIELD_WRAPPER_FUNC:
                    self._log_debug(stmt, f'Skipping already wrapped field "{lvalue.name}"')
                    continue

            # If we're still here, we might actually have a validataclass field definition that we care about!
            # Wrap it in the virtual field wrapper function.
            self._log_debug(stmt, f'Wrapping field "{lvalue.name}" with rvalue', stmt.rvalue)
            stmt.rvalue = self._wrap_in_virtual_field_wrapper(stmt.rvalue)

        # Let the default mypy plugin for dataclasses process the validataclass too.
        # This is needed to get auto-generated methods like __init__ right.
        # TODO: Currently, all fields will be seen as optional by the dataclass plugin, because every assignment has
        #   a right-hand side. We either need to hook into the dataclass plugin, or modify the generated __init__
        #   function, or generate the __init__ function all by ourselves.
        return dataclass_class_maker_callback(self._ctx)

    def _wrap_in_virtual_field_wrapper(self, rvalue: Expression) -> CallExpr:
        """
        Wrap an expression (the right-hand side of an assignment in a validataclass) in a CallExpr for the virtual
        field wrapper function.
        """
        # TODO: We probably don't need to recreate the FuncDef everytime. Make it reusable.
        virtual_wrapper_funcdef = FuncDef(
            name=VIRTUAL_FIELD_WRAPPER_FUNC_NAME,
            arguments=[
                Argument(Var('args'), None, None, ArgKind.ARG_POS),
            ],
            typ=CallableType(
                arg_types=[AnyType(TypeOfAny.implementation_artifact)],
                arg_kinds=[ArgKind.ARG_POS],
                arg_names=['args'],
                # TODO: Does the UnboundType make sense as a placeholder? We will always replace the return type anyway,
                #  but an UnboundType or similar might help us find errors where we the return type wasn't replaced.
                #  Maybe UninhabitedType (i.e. Never) would work for that too.
                ret_type=UnboundType('UNKNOWN_TYPE'),
                fallback=self._api.named_type('builtins.function'),
                name=VIRTUAL_FIELD_WRAPPER_FUNC_NAME,
            ),
        )

        # Generate a call expression for the virtual field wrapper
        virtual_wrapper_nameexpr = NameExpr(VIRTUAL_FIELD_WRAPPER_FUNC_NAME)
        virtual_wrapper_nameexpr.fullname = VIRTUAL_FIELD_WRAPPER_FUNC
        virtual_wrapper_nameexpr.node = virtual_wrapper_funcdef
        virtual_wrapper_nameexpr.kind = GDEF

        virtual_call_expr = CallExpr(
            callee=virtual_wrapper_nameexpr,
            args=[rvalue],
            arg_kinds=[ArgKind.ARG_POS],
            arg_names=[None],
        )
        virtual_call_expr.set_line(rvalue)
        return virtual_call_expr
