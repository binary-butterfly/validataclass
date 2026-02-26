"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, Iterator

from mypy.errorcodes import ErrorCode
from mypy.nodes import (
    Argument,
    ArgKind,
    AssignmentStmt,
    Block,
    CallExpr,
    ClassDef,
    Context,
    Expression,
    FuncDef,
    GDEF,
    ListExpr,
    NameExpr,
    StrExpr,
    TempNode,
    Var,
)
from mypy.plugin import ClassDefContext, SemanticAnalyzerPluginInterface
from mypy.plugins.dataclasses import dataclass_class_maker_callback, DATACLASS_FIELD_SPECIFIERS
from mypy.server.trigger import make_wildcard_trigger
from mypy.types import AnyType, CallableType, TypeOfAny, UnboundType
from typing_extensions import override

from .constants import (
    ERROR_CODE_VALIDATACLASS,
    VALIDATACLASS_FIELD_FUNC,
    VIRTUAL_FIELD_WRAPPER_FUNC,
    VIRTUAL_FIELD_WRAPPER_FUNC_NAME,
)
from .helpers import DebugLogger


class ValidataclassField:
    """
    Internal representation of a validataclass field in the semantic analysis pass, storing information and references
    to expressions for analysis.
    """

    # The name of the field
    name: str

    # Fully qualified names of base validataclasses in which this field has been defined or overridden, in reverse MRO
    # (oldest class first). Does not include the current class, nor base classes that are not validataclasses.
    # Empty for fields that have been created in the current class and don't exist in any base class.
    base_classes: list[str]

    # Assignment statement for this field from the class body.
    # None if the field is not defined explicitly in the current class (i.e. it has only been defined in base classes).
    assignment_stmt: AssignmentStmt | None

    def __init__(self, name: str):
        self.name = name
        self.base_classes = []
        self.assignment_stmt = None

    @override
    def __repr__(self) -> str:
        return f'ValidataclassField({self.name})'

    @property
    def lvalue(self) -> NameExpr:
        """
        NameExpr of the field name, i.e. the left-hand side of the assignment statement.
        """
        assert self.assignment_stmt is not None
        lvalue = self.assignment_stmt.lvalues[0]
        assert isinstance(lvalue, NameExpr)
        return lvalue

    @property
    def lvalue_var(self) -> Var:
        """
        Variable symbol that the lvalue NameExpr references.
        """
        # We can assume that the node is always a Var.
        lvalue_node = self.lvalue.node
        assert lvalue_node is not None and isinstance(lvalue_node, Var)
        return lvalue_node

    @property
    def rvalue(self) -> Expression:
        """
        Right-hand side expression of the assignment statement.
        """
        assert self.assignment_stmt is not None
        return self.assignment_stmt.rvalue

    def serialize(self) -> dict[str, str]:
        """
        Serialize this object to save it in a ClassDef's metadata (potentially cached by mypy).
        Currently only contains the field name.
        """
        return {
            "name": self.name,
        }


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

    # FuncDef for the virtual field wrapper function. Created on first use and cached here as a class variable.
    _virtual_field_wrapper_funcdef: FuncDef | None = None

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
        # Collect all validataclass fields in this class, including fields defined in base classes
        current_fields = self._collect_fields()
        if current_fields is None:
            return False

        # Iterate over all fields and modify the assignment statements
        for field in current_fields:
            # Skip fields that haven't been defined in this class (i.e. only in base classes)
            if field.assignment_stmt is None:
                continue

            # Update the class definition for this field (wrap assignment rvalue and add virtual attribute)
            self._transform_field_in_class(field)

        # Store information about all fields (for now, only their names) in the class metadata for subclasses
        self._class_def.info.metadata['validataclass'] = {
            'fields': [field.serialize() for field in current_fields if field.assignment_stmt is not None],
        }

        # Let the default mypy plugin for dataclasses process the validataclass too.
        # This is needed to get auto-generated methods like __init__ right.
        # TODO: Currently, all fields will be seen as optional by the dataclass plugin, because every assignment has
        #   a right-hand side. We either need to hook into the dataclass plugin, or modify the generated __init__
        #   function, or generate the __init__ function all by ourselves.
        return dataclass_class_maker_callback(self._ctx)

    def _get_assignment_statements_from_block(self, block: Block) -> Iterator[AssignmentStmt]:
        """
        Iterate over all assignment statements of a block.
        """
        for stmt in block.body:
            if isinstance(stmt, AssignmentStmt):
                yield stmt
            else:
                self._log_debug(stmt, f'Skipping statement of type {type(stmt)}')

    def _collect_fields(self) -> list[ValidataclassField] | None:
        """
        Collect all fields defined in the validataclass and its base classes.
        """
        current_fields: dict[str, ValidataclassField] = {}

        # First, collect all fields defined in subclasses (in reverse MRO, oldest class first)
        for base_typeinfo in reversed(self._class_def.info.mro[1:-1]):
            base_fullname = base_typeinfo.fullname

            # Ignore base classes that are not validataclasses
            if 'validataclass_tag' not in base_typeinfo.metadata:
                self._log_debug(None, f'Skipping base class "{base_fullname}" (no validataclass tag)')
                continue

            # Ensure base class has already been processed by this plugin, otherwise we need another pass
            if 'validataclass' not in base_typeinfo.metadata:
                self._log_debug(None, f'Base class "{base_fullname}" not processsed yet, need another pass')
                return None

            # Gather all fields previously collected by this very function when the base class was analyzed
            for field_data in base_typeinfo.metadata['validataclass'].get('fields', []):
                field_name: str = field_data['name']

                if field_name not in current_fields:
                    current_fields[field_name] = ValidataclassField(field_name)

                # Construct list of base classes that define this field
                current_fields[field_name].base_classes.append(base_fullname)

            # Set dependency so that changing the base class will trigger reprocessing of this class
            self._api.add_plugin_dependency(make_wildcard_trigger(base_fullname))

        # Second, collect fields that have been defined in this class (update existing fields if necessary) by
        # iterating over all assignment statements in the class body
        for stmt in self._get_assignment_statements_from_block(self._class_def.defs):
            # TODO: Handle InitVars?

            # The validataclass decorator ignores attributes without annotations (in most cases)
            if not stmt.new_syntax:
                # TODO: Unless the attribute starts with an underscore, the decorator actually checks the type of the
                #   RHS of an annotation-less field and raises an error if it contains a validator or default (because
                #   it means you probably forgot the annotation). It's a bit more difficult to check this here though.
                self._log_debug(stmt, f'Skipping assignment for "{stmt.lvalues}" without type annotation')
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
            if isinstance(stmt.rvalue, TempNode) and stmt.rvalue.no_rhs:
                self._fail(
                    'Annotated field without assignment (missing Validator or BaseDefault on right-hand side)',
                    stmt,
                )
                continue

            # Handle fields that are already wrapped or created with field specifier functions
            if isinstance(stmt.rvalue, CallExpr) and isinstance(stmt.rvalue.callee, NameExpr):
                callee_name = stmt.rvalue.callee.fullname

                # Ignore fields that have been created with the regular dataclasses.field() or similar
                if callee_name in DATACLASS_FIELD_SPECIFIERS:
                    # TODO: Handle these properly.
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
            if lvalue.name not in current_fields:
                current_fields[lvalue.name] = ValidataclassField(lvalue.name)
            current_fields[lvalue.name].assignment_stmt = stmt

        return list(current_fields.values())

    def _transform_field_in_class(self, field: ValidataclassField) -> None:
        """
        Update the class definition for a single validataclass field for later analysis.

        This does primarily one thing: Wrap the right-hand side of the field's assignment statement in the virtual field
        wrapper function call (modifying the assignment in place). Additional arguments (class nane, field name, list
        of base classes) are passed to the wrapper.
        """
        assert field.assignment_stmt is not None

        # Allow incompatible overrides of fields in validataclasses
        # TODO: This is necessary because historically we've allowed to override the type of a field in an incompatible
        #   way in a subclass. This actually isn't very type-safe, though. We probably should discourage this and
        #   provide an option to allow incompatible overrides for compatibility. (Maybe a strict mode for this plugin?)
        field.lvalue_var.allow_incompatible_override = True

        # Wrap the right-hand side of the assignment in a call to the virtual field wrapper function, changing the
        # assignment statement in the class body in-place.
        self._log_debug(field.assignment_stmt, f'Wrapping field "{field.name}" with RHS', field.rvalue)
        field.assignment_stmt.rvalue = self._construct_virtual_wrapper_callexpr(
            field.rvalue,
            field.name,
            field.base_classes,
        )

    def _construct_virtual_wrapper_callexpr(
        self,
        field_rhs: Expression,
        field_name: str,
        base_classes: list[str],
    ) -> CallExpr:
        """
        Construct a CallExpr for the virtual field wrapper function with the given expressions as arguments.

        First argument: Right-hand side expression of the field assignment.
        Second argument: Fully qualified name of the current class.
        Third argument: Name of the field.
        Fourth argument: List of the fully qualified names of all base classes that define this field (in reverse MRO).
        """
        cls = type(self)

        # Create the virtual wrapper FuncDef only once and cache it as a class variable
        if cls._virtual_field_wrapper_funcdef is None:
            any_type = AnyType(TypeOfAny.explicit)
            cls._virtual_field_wrapper_funcdef = FuncDef(
                name=VIRTUAL_FIELD_WRAPPER_FUNC_NAME,
                arguments=[
                    Argument(Var('field_rhs'), any_type, None, ArgKind.ARG_POS),
                    Argument(Var('class_name'), any_type, None, ArgKind.ARG_POS),
                    Argument(Var('field_name'), any_type, None, ArgKind.ARG_POS),
                    Argument(Var('base_classes'), any_type, None, ArgKind.ARG_POS),
                ],
                typ=CallableType(
                    name=VIRTUAL_FIELD_WRAPPER_FUNC_NAME,
                    arg_types=[any_type, any_type, any_type, any_type],
                    arg_kinds=[ArgKind.ARG_POS, ArgKind.ARG_POS, ArgKind.ARG_POS, ArgKind.ARG_POS],
                    arg_names=['field_rhs', 'class_name', 'field_name', 'base_classes'],
                    # Return type will always be overridden by the function hook, so this one doesn't matter too much.
                    # We use an UnboundType because if it ever slips through, mypy should complain about it.
                    ret_type=UnboundType('UNKNOWN_TYPE'),
                    fallback=self._api.named_type('builtins.function'),
                ),
            )

        # Generate a call expression for the virtual field wrapper
        virtual_wrapper_nameexpr = NameExpr(VIRTUAL_FIELD_WRAPPER_FUNC_NAME)
        virtual_wrapper_nameexpr.fullname = VIRTUAL_FIELD_WRAPPER_FUNC
        virtual_wrapper_nameexpr.node = cls._virtual_field_wrapper_funcdef
        virtual_wrapper_nameexpr.kind = GDEF

        virtual_call_expr = CallExpr(
            callee=virtual_wrapper_nameexpr,
            args=[
                field_rhs,
                StrExpr(self._class_def.fullname),
                StrExpr(field_name),
                ListExpr([StrExpr(base_class) for base_class in base_classes]),
            ],
            arg_kinds=[ArgKind.ARG_POS, ArgKind.ARG_POS, ArgKind.ARG_POS, ArgKind.ARG_POS],
            arg_names=[None, None, None, None],
        )
        virtual_call_expr.set_line(field_rhs)
        return virtual_call_expr
