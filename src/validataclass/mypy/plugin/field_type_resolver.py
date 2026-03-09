"""
validataclass
Copyright (c) 2026, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

from typing import Any, cast

from mypy.errorcodes import ErrorCode
from mypy.nodes import ArgKind, CallExpr, Context, Expression, ListExpr, MemberExpr, StrExpr, TempNode, RefExpr
from mypy.plugin import CheckerPluginInterface, FunctionContext
from mypy.typeops import make_simplified_union
from mypy.types import (
    AnyType,
    CallableType,
    Instance,
    Overloaded,
    ProperType,
    TupleType,
    Type,
    TypeOfAny,
    UninhabitedType,
    get_proper_type,
)

from .constants import FIELD_DEFAULT_BASE_CLASS, VALIDATACLASS_FIELD_FUNCS, VALIDATOR_BASE_CLASS
from .error_codes import ERROR_CODE_VALIDATACLASS, ERROR_CODE_VALIDATACLASS_EMPTY_TYPE
from .debug_logger import DebugLogger
from .parsed_field_cache import ParsedFieldCache, ParsedValidataclassField


class FieldTypeResolver:
    """
    Handler for function hook to analyse the wrapped expression in virtual field wrapper calls, i.e. the right-hand side
    expressions of assignments in a validataclass.
    """

    _ctx: FunctionContext

    # Interface to mypy's type checker
    _api: CheckerPluginInterface

    # Logger for plugin development and debugging
    _logger: DebugLogger

    # Internal cache for parsed validataclass fields (i.e. parsed types), shared across instances of this class
    _parsed_field_cache: ParsedFieldCache

    def __init__(self, ctx: FunctionContext, logger: DebugLogger, parsed_field_cache: ParsedFieldCache):
        self._ctx = ctx
        self._api = ctx.api
        self._logger = logger
        self._parsed_field_cache = parsed_field_cache

    def _get_logger_context(self) -> str:
        """
        Return a string representation of the current context, i.e. the file path and line number of this call.
        """
        return f'{self._api.path}:{self._ctx.context.line}'

    def _log_warn(self, msg: str, *objects: Any) -> None:  # pragma: nocover
        """
        Log a message on WARN level.

        This should only be used during plugin development to warn about unhandled expressions/types. In real code,
        please use `_fail` or `_fail_not_implemented` (see ValidataclassTransformer) instead, which result in actual
        mypy errors.
        """
        return self._logger.log('WARN', self._get_logger_context(), msg, *objects)

    def _log_debug(self, msg: str, *objects: Any) -> None:
        """
        Log a message on DEBUG level. Only printed if debug mode is enabled.
        Use this for better traceability and debugging of what the plugin is doing.
        """
        return self._logger.log('DEBUG', self._get_logger_context(), msg, *objects)

    def _fail(self, msg: str, context: Context | None = None, *, code: ErrorCode | None = None) -> None:
        """
        Report a mypy error to the user. Default code is "validataclass".
        """
        self._api.fail(
            msg,
            context or self._ctx.context,
            code=code or ERROR_CODE_VALIDATACLASS,
        )

    def resolve(self) -> Type:
        """
        Analyze the wrapped expression (right-hand side of a validataclass field assignment) to find validator and
        default objects within it and determine the type that this field can have, taking base classes into account.

        Return the expected field type by combining the validator result type and the default value type.
        """
        # Parse call arguments of the virtual field wrapper call
        field_rhs_expr, class_name, field_name, base_classes = self._get_call_args()

        # Parse entire field definition (parse RHS expression and merge with parsed fields from base classes)
        parsed_field = self._parse_field_definition(field_name, field_rhs_expr, base_classes)

        # Store parsed types in internal cache (not persisted between mypy runs!)
        self._parsed_field_cache.set_field(class_name, field_name, parsed_field)

        # Stop here if there was an error parsing the tuple (fallback to returning Any)
        if parsed_field.error:
            return AnyType(TypeOfAny.from_error)

        # Get the combined type of the field (union of validated type and default type)
        resolved_type = self._resolve_field_type(parsed_field)
        self._log_debug('Resolved type of field "{field_name}"', resolved_type)

        # Handle edge case where resolved type is the empty type (i.e. Never). The most likely cause for this (which is
        # not "user does weird stuff") is that the field uses a RejectValidator (or similar, anything where validate()
        # never returns) and does not have a default value. A validataclass with this field *can* be instantiated
        # manually (if the field type is anything other than Never), but a DataclassValidator would never return.
        # If we return resolved_type here, mypy will mark the class as unreachable code. Instead, we report an error
        # and return an Any type.
        if isinstance(resolved_type, UninhabitedType):
            self._fail(
                f'Dataclass can never be validated, validator and default have empty type "{resolved_type}" (did you '
                'forget a default value?)',
                code=ERROR_CODE_VALIDATACLASS_EMPTY_TYPE,
            )
            return AnyType(TypeOfAny.from_error)

        return resolved_type

    def _get_call_args(self) -> tuple[Expression, str, str, list[str]]:
        """
        Parse the call argument expressions of the virtual field wrapper call.
        Return a tuple with the field RHS expression, the class name, the field name and a list of base class names.
        """
        # We can assume that every call to the virtual field wrapper was constructed by us, and that every call has
        # the expected number of arguments, so using assert is safe here.
        assert len(self._ctx.args) == 4, 'Virtual field wrapper was called with invalid number of arguments'
        assert all(len(arg) == 1 for arg in self._ctx.args)

        return (
            # First argument: Wrapped right-hand side expression of the validataclass field assignment statement
            self._ctx.args[0][0],

            # Second argument: String expression, fully qualified name of the current class
            self._get_call_arg_as_str(1),

            # Third argument: String expression, name of the field
            self._get_call_arg_as_str(2),

            # Fourth argument: List expression with string expressions, names of base classes that define this field.
            self._get_call_arg_as_list_of_str(3),
        )

    def _get_call_arg_as_str(self, arg_number: int) -> str:
        """
        Parse the n-th call argument as a StrExpr and return the string value.
        """
        expr = self._ctx.args[arg_number][0]
        assert isinstance(expr, StrExpr)
        return expr.value

    def _get_call_arg_as_list_of_str(self, arg_number: int) -> list[str]:
        """
        Parse the n-th call argument as a ListExpr containing StrExprs and return a list of the string values.
        """
        expr = self._ctx.args[arg_number][0]
        assert isinstance(expr, ListExpr)
        assert all(isinstance(item, StrExpr) for item in expr.items)
        return [cast(StrExpr, item).value for item in expr.items]

    def _parse_field_definition(
        self,
        field_name: str,
        field_rhs_expr: Expression,
        base_classes: list[str],
    ) -> ParsedValidataclassField:
        """
        Analyze the entire field definition, starting by collecting the validator and default types of all base classes
        (by retrieving the ParsedValidataclasFields from the parsed field cache), then analyzing the right-hand side
        expression of the current field assignment and merging the results.
        """
        # First of all, check if the field was created explicitly using validataclass_field(), i.e. the right-hand side
        # is a call to that function. Since this functions are not dependent on base classes (they always replace the
        # entire field definition), we can shortcut the analysis here.
        # (Fields created with dataclasses.field() are skipped by the ValidataclassTransformer.)
        if isinstance(field_rhs_expr, CallExpr) and isinstance(field_rhs_expr.callee, RefExpr):
            # Handle fields created explicitly using validataclass_field()
            if field_rhs_expr.callee.fullname in VALIDATACLASS_FIELD_FUNCS:
                return self._parse_validataclass_field_callexpr(field_rhs_expr)

        # This will hold the end result that's returned at the end of the function
        fully_parsed_field = ParsedValidataclassField()

        # First, retrieve the parsed field of all base classes from our cache, starting with the "oldest" class
        for base_class in base_classes:
            base_parsed_field = self._parsed_field_cache.get_field(base_class, field_name)

            # If there was an error when the field in the base class was parsed, set the error flag for later, then
            # ignore the base class and continue.
            if base_parsed_field.error:
                fully_parsed_field.error = True
            else:
                # Overwrite validator and default, but only if they are defined in the expression
                fully_parsed_field.merge(base_parsed_field)

        # Report an error if one of the base classes had an error. We don't need a more specific error message here
        # because the error should have already been reported when the base class was analyzed. We will continue parsing
        # the field so that specific errors in this class are reported, but the user should know that parsing is
        # incomplete because of a prior error.
        if fully_parsed_field.error:
            self._fail('Field cannot be fully parsed because of a prior error in one of the base classes')

        # Now, parse the right-hand side expression of the assignment in the current class and merge the result
        self._log_debug(f'Parse field "{field_name}" with RHS expression', field_rhs_expr)
        assignment_parsed_field = self._parse_rhs_expression(field_rhs_expr)
        fully_parsed_field.merge(assignment_parsed_field)

        # Make sure that the field has a validator instance (if there was no other error yet)
        if not fully_parsed_field.error and fully_parsed_field.validator_type is None:
            fully_parsed_field.error = True
            self._fail('No Validator found in field definition')

        return fully_parsed_field

    def _parse_rhs_expression(self, rhs_expr: Expression) -> ParsedValidataclassField:
        """
        Analyze the right-hand side expression of a validataclass field, determining its type based on validator and
        default objects found in the type of the expression.
        """
        # Get type of field assignment RHS
        rhs_type = get_proper_type(self._api.get_expression_type(rhs_expr))

        parsed_field = ParsedValidataclassField()

        if isinstance(rhs_type, TupleType):
            # We have a tuple on the right-hand side, probably a tuple with validator and default object
            for item_type in rhs_type.items:
                item_type = get_proper_type(item_type)
                self._parse_rhs_item(item_type, parsed_field)
        else:
            # We have a single Instance on the right-hand side, probably a validator or default object
            self._parse_rhs_item(rhs_type, parsed_field)

        return parsed_field

    def _parse_rhs_item(self, item_type: Type, parsed_field: ParsedValidataclassField) -> None:
        """
        Analyze the type of a single item in the right-hand side of a validataclass field, i.e. an item in a tuple or
        the whole right-hand side if it's not a tuple.

        The result will be written into the given ParsedValidataclassField. May report errors, e.g. for unknown types or
        for another validator/default instance if the parsed field already has one.
        """
        item_type = get_proper_type(item_type)

        # Usually we're expecting an instance of class here, namely of a validator class or default class
        if isinstance(item_type, Instance):
            # Check for validator instances (base class Validator)
            if item_type.type.has_base(VALIDATOR_BASE_CLASS):
                # Make sure only one validator is set
                if parsed_field.validator_type is not None:
                    parsed_field.error = True
                    self._fail('Multiple validator instances found in field definition')
                    return

                # Store type of validator for later
                self._log_debug(f'  - Validator type: {item_type}')
                parsed_field.validator_type = item_type
                return

            # Check for default instances (base class BaseDefault)
            if item_type.type.has_base(FIELD_DEFAULT_BASE_CLASS):
                # Make sure only one default object is set
                if parsed_field.default_type is not None:
                    parsed_field.error = True
                    self._fail('Multiple default objects found in field definition')
                    return

                # Store type of default object for later
                self._log_debug(f'  - Default type: {item_type}')
                parsed_field.default_type = item_type
                return

        # (Everything else is probably an error!)

        # One easy mistake is writing a validator class name without parentheses (e.g. `field: int = IntegerValidator`).
        # Let's provide a more helpful error message (the default string representation would be long and confusing).
        item_type_str = str(item_type)
        if isinstance(item_type, CallableType):
            callable_ret_type = get_proper_type(item_type.ret_type)
            item_type_str = f'Callable[..., {callable_ret_type}]'

            # Check if the callable's return type is a validator instance
            if isinstance(callable_ret_type, Instance) and callable_ret_type.type.has_base(VALIDATOR_BASE_CLASS):
                parsed_field.error = True
                self._fail(
                    f'Unexpected type "{item_type_str}" in field definition (did you mean '
                    f'"{callable_ret_type.type.name}()"?)'
                )
                return

        # Fallback to unexpected type error
        parsed_field.error = True
        self._fail(f'Unexpected type "{item_type_str}" in field definition (expected Validator or BaseDefault)')

    def _parse_validataclass_field_callexpr(self, call_expr: CallExpr) -> ParsedValidataclassField:
        """
        Analyze a `validataclass_field()` call expression to find validator and default objects.
        """
        parsed_field = ParsedValidataclassField()

        # Iterate over call arguments, differentiate positional and named arguments, find validator and default
        for i in range(len(call_expr.args)):
            # Get argument expression, kind (positional/named) and name (None for positional arguments)
            arg_expr = call_expr.args[i]
            arg_kind = call_expr.arg_kinds[i]
            arg_name = call_expr.arg_names[i]

            # Get type of argument expression
            arg_type = get_proper_type(self._api.get_expression_type(arg_expr))

            # NOTE: We can ignore a lot of possible errors here that are already covered by mypy itself, e.g. too many
            # arguments, duplicate arguments, incorrect argument types, etc. We still have to check for these errors
            # (because it means the call is invalid and can't be parsed correctly), but we don't need to report them.

            # The function has only a single positional argument, which is the validator. We can also assume that all
            # positional arguments come first (otherwise it's a syntax error and we don't even reach this code).
            if (arg_kind == ArgKind.ARG_POS and i == 0) or arg_name == 'validator':
                # There can only be one validator (mypy will report an error for this)
                if parsed_field.validator_type is not None:
                    parsed_field.error = True
                    break

                # Ensure that argument is a Validator instance (mypy will report an error otherwise)
                if not isinstance(arg_type, Instance) or not arg_type.type.has_base(VALIDATOR_BASE_CLASS):
                    parsed_field.error = True
                    break

                # Store type of validator for later
                parsed_field.validator_type = arg_type
                continue

            # Check for named arguments (unknown arguments can be ignored here)
            match arg_name:
                # Check for field default argument
                case 'default':
                    # There can only be one default (mypy will report an error for this)
                    if parsed_field.default_type is not None:
                        parsed_field.error = True
                        break

                    # Ensure that argument is a BaseDefault instance (mypy will report an error otherwise)
                    # NOTE: Using raw defaults and dataclasses.MISSING here has been deprecated, so we don't need to
                    # support them. mypy will report a deprecation warning, we just treat it as an error and return Any.
                    if not isinstance(arg_type, Instance) or not arg_type.type.has_base(FIELD_DEFAULT_BASE_CLASS):
                        parsed_field.error = True
                        break

                    # Store type of default object for later
                    parsed_field.default_type = arg_type

                # Validataclass fields are required to be init fields, so the argument isn't allowed
                case 'init':
                    # Report error but continue parsing, because this argument wouldn't influence the field type
                    self._fail('Keyword argument "init" is not allowed in validataclass_field')

                # Validataclass fields should use a DefaultFactory instead of the default_factory argument
                case 'default_factory':
                    # Report error and stop parsing, because the argument related to the field default
                    self._fail(
                        'Keyword argument "default_factory" is not allowed in validataclass_field; use '
                        'default=DefaultFactory(...) instead'
                    )
                    parsed_field.error = True
                    break

        # Stop checking if there were errors parsing the arguments
        if parsed_field.error:
            return parsed_field

        # Ensure that the field has a validator
        if parsed_field.validator_type is None:
            parsed_field.error = True
            self._fail('No validator found in validataclass_field() call')

        return parsed_field

    def _resolve_field_type(self, parsed_field: ParsedValidataclassField) -> ProperType:
        """
        Resolve the type of the parsed field by determining the result type of the validator and default objects and
        combining them in a type union.
        """
        assert parsed_field.validator_type is not None, 'No validator. This should have been caught earlier!'

        # Determine the result type of the validator (i.e. the return type of its validate method)
        validator_result_type = self._get_method_return_type(parsed_field.validator_type, 'validate')

        # Determine the result type of the default object (i.e. the return type of its get_value method)
        if parsed_field.default_type is not None:
            default_result_type = self._get_method_return_type(parsed_field.default_type, 'get_value')
        else:
            # UninhabitedType is the bottom type (Never/NoReturn), meaning there is no default value
            default_result_type = UninhabitedType()

        # Combine result types of validator and default object
        return make_simplified_union(
            [validator_result_type, default_result_type],
            line=self._ctx.context.line,
            column=self._ctx.context.column,
        )

    def _get_method_return_type(self, instance_type: Instance, method_name: str) -> ProperType:
        """
        Construct a MemberExpr for the given instance type and method name, resolve expression type and return the
        return type of the method. Report an error if it's not a valid callable.

        In other words, returns the return type of `instance.method_name()`.
        """
        # We don't need to construct an actual CallExpr here, the MemberExpr is enough. Evaluating a CallExpr type can
        # have side effects, like mypy falsely reporting "code unreachable" if we have a RejectValidator or NoDefault.
        constructed_memberexpr = MemberExpr(TempNode(instance_type), method_name)
        constructed_method_type = get_proper_type(
            self._api.get_expression_type(constructed_memberexpr)
        )

        # Special case: It's an overloaded method. Combine all possible return types in a union.
        if isinstance(constructed_method_type, Overloaded):
            return make_simplified_union(
                [item.ret_type for item in constructed_method_type.items],
                line=self._ctx.context.line,
                column=self._ctx.context.column,
            )

        # Make sure it's a callable. If it isn't, either we forgot some edge case, or the user is doing something *very*
        # weird (namely overriding validate or get_value to be something that's not callable, which mypy should notice
        # anyway). We should report an error here, but can return a Never type as if the validator/default didn't exist.
        if not isinstance(constructed_method_type, CallableType):
            self._fail(f'"{instance_type.type.name}.{method_name}" is not a callable')
            return UninhabitedType()

        return get_proper_type(constructed_method_type.ret_type)
