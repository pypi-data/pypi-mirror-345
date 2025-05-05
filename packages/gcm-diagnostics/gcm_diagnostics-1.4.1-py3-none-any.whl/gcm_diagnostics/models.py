from __future__ import annotations

from collections.abc import Collection
from enum import Enum, StrEnum
from http import HTTPStatus
from typing import Any, ClassVar, Generic, Literal, Optional, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, SerializeAsAny, create_model

Loc = list[str | int]


class BaseModel(PydanticBaseModel):
    """
    Base model for the diagnostic pydantic models.
    """

    model_config = ConfigDict(extra="forbid")


class GenericError(BaseModel):
    """Generic error model compatible with pydantic diagnostics."""

    loc: Loc = Field(default_factory=list, title="Error location.")
    msg: str = Field(title="Descriptive human readable error message")
    type: str = Field(title="Error type identifier")


class DiagnosticError(GenericError):
    """
    Base class for all diagnostic errors.
    """

    model_config = ConfigDict(extra="allow")

    # This is intentionally protected, as Pydantic does not export protected members to OpenAPI schema,
    # and that is exactly what we want. Status code is not part of the JSON response, but it represents
    # HTTP status code of the error response.
    status_code: ClassVar[int] = HTTPStatus.UNPROCESSABLE_ENTITY

    loc: Loc = Field(default_factory=list, title="Error location")
    msg: str = Field(title="Descriptive human readable error message")
    type: str = Field(title="Error type identifier")


T = TypeVar("T", bound=GenericError)


class DiagnosticResponse(BaseModel, Generic[T]):
    """
    Response returned to user, when any diagnostic error is collected.
    """

    detail: list[SerializeAsAny[T]] = Field(default_factory=list)


class ModelValidationError(GenericError):
    """Base class describing Pydantic validation error."""

    ctx: Optional[dict[str, Any]] = Field(
        None, description="An optional object which contains values required to render the error message."
    )
    input: Any = Field(description="The input provided for validation.")


class PydanticError(str, Enum):
    """Enum containing all known pydantic error types, to get rid of magic constants."""

    ARGUMENTS_TYPE = "arguments_type"
    ASSERTION_ERROR = "assertion_error"
    BOOL_PARSING = "bool_parsing"
    BOOL_TYPE = "bool_type"
    BYTES_INVALID_ENCODING = "bytes_invalid_encoding"
    BYTES_TOO_LONG = "bytes_too_long"
    BYTES_TOO_SHORT = "bytes_too_short"
    BYTES_TYPE = "bytes_type"
    CALLABLE_TYPE = "callable_type"
    COMPLEX_STR_PARSING = "complex_str_parsing"
    COMPLEX_TYPE = "complex_type"
    DATACLASS_EXACT_TYPE = "dataclass_exact_type"
    DATACLASS_TYPE = "dataclass_type"
    DATE_FROM_DATETIME_INEXACT = "date_from_datetime_inexact"
    DATE_FROM_DATETIME_PARSING = "date_from_datetime_parsing"
    DATE_FUTURE = "date_future"
    DATE_PARSING = "date_parsing"
    DATE_PAST = "date_past"
    DATE_TYPE = "date_type"
    DATETIME_FROM_DATE_PARSING = "datetime_from_date_parsing"
    DATETIME_FUTURE = "datetime_future"
    DATETIME_OBJECT_INVALID = "datetime_object_invalid"
    DATETIME_PARSING = "datetime_parsing"
    DATETIME_PAST = "datetime_past"
    DATETIME_TYPE = "datetime_type"
    DECIMAL_MAX_DIGITS = "decimal_max_digits"
    DECIMAL_MAX_PLACES = "decimal_max_places"
    DECIMAL_PARSING = "decimal_parsing"
    DECIMAL_TYPE = "decimal_type"
    DECIMAL_WHOLE_DIGITS = "decimal_whole_digits"
    DICT_TYPE = "dict_type"
    ENUM = "enum"
    EXTRA_FORBIDDEN = "extra_forbidden"
    FINITE_NUMBER = "finite_number"
    FLOAT_PARSING = "float_parsing"
    FLOAT_TYPE = "float_type"
    FROZEN_FIELD = "frozen_field"
    FROZEN_INSTANCE = "frozen_instance"
    FROZEN_SET_TYPE = "frozen_set_type"
    GET_ATTRIBUTE_ERROR = "get_attribute_error"
    GREATER_THAN = "greater_than"
    GREATER_THAN_EQUAL = "greater_than_equal"
    INT_FROM_FLOAT = "int_from_float"
    INT_PARSING = "int_parsing"
    INT_PARSING_SIZE = "int_parsing_size"
    INT_TYPE = "int_type"
    INVALID_KEY = "invalid_key"
    IS_INSTANCE_OF = "is_instance_of"
    IS_SUBCLASS_OF = "is_subclass_of"
    ITERABLE_TYPE = "iterable_type"
    ITERATION_ERROR = "iteration_error"
    JSON_INVALID = "json_invalid"
    JSON_TYPE = "json_type"
    LESS_THAN = "less_than"
    LESS_THAN_EQUAL = "less_than_equal"
    LIST_TYPE = "list_type"
    LITERAL_ERROR = "literal_error"
    MAPPING_TYPE = "mapping_type"
    MISSING = "missing"
    MISSING_ARGUMENT = "missing_argument"
    MISSING_KEYWORD_ONLY_ARGUMENT = "missing_keyword_only_argument"
    MISSING_POSITIONAL_ONLY_ARGUMENT = "missing_positional_only_argument"
    MODEL_ATTRIBUTES_TYPE = "model_attributes_type"
    MODEL_TYPE = "model_type"
    MULTIPLE_ARGUMENT_VALUES = "multiple_argument_values"
    MULTIPLE_OF = "multiple_of"
    NEEDS_PYTHON_OBJECT = "needs_python_object"
    NO_SUCH_ATTRIBUTE = "no_such_attribute"
    NONE_REQUIRED = "none_required"
    RECURSION_LOOP = "recursion_loop"
    SET_TYPE = "set_type"
    STRING_PATTERN_MISMATCH = "string_pattern_mismatch"
    STRING_SUB_TYPE = "string_sub_type"
    STRING_TOO_LONG = "string_too_long"
    STRING_TOO_SHORT = "string_too_short"
    STRING_TYPE = "string_type"
    STRING_UNICODE = "string_unicode"
    TIME_DELTA_PARSING = "time_delta_parsing"
    TIME_DELTA_TYPE = "time_delta_type"
    TIME_PARSING = "time_parsing"
    TIME_TYPE = "time_type"
    TIMEZONE_AWARE = "timezone_aware"
    TIMEZONE_NAIVE = "timezone_naive"
    TOO_LONG = "too_long"
    TOO_SHORT = "too_short"
    TUPLE_TYPE = "tuple_type"
    UNEXPECTED_KEYWORD_ARGUMENT = "unexpected_keyword_argument"
    UNEXPECTED_POSITIONAL_ARGUMENT = "unexpected_positional_argument"
    UNION_TAG_INVALID = "union_tag_invalid"
    UNION_TAG_NOT_FOUND = "union_tag_not_found"
    URL_PARSING = "url_parsing"
    URL_SCHEME = "url_scheme"
    URL_SYNTAX_VIOLATION = "url_syntax_violation"
    URL_TOO_LONG = "url_too_long"
    URL_TYPE = "url_type"
    UUID_PARSING = "uuid_parsing"
    UUID_TYPE = "uuid_type"
    UUID_VERSION = "uuid_version"
    VALUE_ERROR = "value_error"


# Mapping of Pydantic error types to respective error descriptions (taken from Pydantic documentation at
# https://docs.pydantic.dev/latest/errors/validation_errors/). This is here just to provide user-friendly documentation for
# pydantic error types in OpenAPI schema as currently there is no curated structure in pydantic source code, that can be used
# for this.
ALL_PYDANTIC_ERROR_TYPES: dict[PydanticError, str] = {
    PydanticError.ARGUMENTS_TYPE: "Invalid type for arguments.",
    PydanticError.ASSERTION_ERROR: "This error is raised when a failing `assert` statement is encountered during validation.",
    PydanticError.BOOL_PARSING: "This error is raised when the input value is a string that is not valid for coercion to a "
    "boolean.",
    PydanticError.BOOL_TYPE: "This error is raised when the input value's type is not valid for a `bool` field.",
    PydanticError.BYTES_INVALID_ENCODING: "This error is raised when a `bytes` value is invalid under the configured encoding.",
    PydanticError.BYTES_TOO_LONG: "This error is raised when a `bytes` value is longer than the configured maximum length.",
    PydanticError.BYTES_TOO_SHORT: "This error is raised when a `bytes` value is shorter than the configured minimum length.",
    PydanticError.BYTES_TYPE: "This error is raised when the input value's type is not valid for a `bytes` field.",
    PydanticError.CALLABLE_TYPE: "This error is raised when the input value's type is not valid for a `callable` field.",
    PydanticError.COMPLEX_STR_PARSING: "This error is raised when the input value is a string but cannot be parsed as a complex "
    "number.",
    PydanticError.COMPLEX_TYPE: "This error is raised when the input value's type is not valid for a `complex` field.",
    PydanticError.DATACLASS_EXACT_TYPE: "This error is raised when validating a dataclass with `strict=True` and the input is "
    "not an instance of the dataclass.",
    PydanticError.DATACLASS_TYPE: "This error is raised when the input value's type is not valid for a `dataclass` field.",
    PydanticError.DATE_FROM_DATETIME_INEXACT: "This error is raised when a `date` value is created from a `datetime` value that "
    "is not at midnight. For a timestamp to parse into a field of type `date`, the "
    "time components must all be zero.",
    PydanticError.DATE_FROM_DATETIME_PARSING: "This error is raised when the input value is a string that cannot be parsed for a "
    "date field.",
    PydanticError.DATE_FUTURE: "This error is raised when the input value provided for a `FutureDate` field is not in the "
    "future.",
    PydanticError.DATE_PARSING: "This error is raised when validating JSON where the input value is string that cannot be parsed "
    "for a date field.",
    PydanticError.DATE_PAST: "This error is raised when the value provided for a `PastDate` field is not in the past.",
    PydanticError.DATE_TYPE: "This error is raised when the input value's type is not valid for a `date` field.",
    PydanticError.DATETIME_FROM_DATE_PARSING: "This error is raised when the input value is a string that cannot be parsed for "
    "a `datetime` field.",
    PydanticError.DATETIME_FUTURE: "This error is raised when the input value provided for a `FutureDatetime` field is not in "
    "the future.",
    PydanticError.DATETIME_OBJECT_INVALID: "This error is raised when something about the `datetime` object is not valid.",
    PydanticError.DATETIME_PARSING: "This error is raised when the input value is a string that cannot be parsed for a "
    "`datetime` field.",
    PydanticError.DATETIME_PAST: "This error is raised when the value provided for a `PastDatetime` field is not in the past.",
    PydanticError.DATETIME_TYPE: "This error is raised when the input value's type is not valid for a `datetime` field.",
    PydanticError.DECIMAL_MAX_DIGITS: "This error is raised when a `Decimal` value has more digits than the configured maximum.",
    PydanticError.DECIMAL_MAX_PLACES: "This error is raised when the value provided for a `Decimal` has too many digits after "
    "the decimal point.",
    PydanticError.DECIMAL_PARSING: "This error is raised when the value provided for a `Decimal` could not be parsed as a "
    "decimal number.",
    PydanticError.DECIMAL_TYPE: "This error is raised when the input value's type is not valid for a `Decimal` field.",
    PydanticError.DECIMAL_WHOLE_DIGITS: "This error is raised when the value provided for a `Decimal` has more digits before "
    "the decimal point than `max_digits - decimal_places` (as long as both are specified).",
    PydanticError.DICT_TYPE: "This error is raised when the input value's type is not valid for a `dict` field.",
    PydanticError.ENUM: "This error is raised when the input value is not a valid `enum` member.",
    PydanticError.EXTRA_FORBIDDEN: "This error is raised when the input value has extra fields that are not allowed.",
    PydanticError.FINITE_NUMBER: "This error is raised when the input value is not a finite number.",
    PydanticError.FLOAT_PARSING: "This error is raised when the input value is a string that cannot be parsed as a float.",
    PydanticError.FLOAT_TYPE: "This error is raised when the input value's type is not valid for a `float` field.",
    PydanticError.FROZEN_FIELD: "This error is raised when trying to set a value on a frozen field or to delete such a field.",
    PydanticError.FROZEN_INSTANCE: "This error is raised when trying to set a value of a field on a frozen instance or to "
    "delete such an field.",
    PydanticError.FROZEN_SET_TYPE: "This error is raised when the input value's type is not valid for a frozenset field.",
    PydanticError.GET_ATTRIBUTE_ERROR: "This error is raised when model_config['from_attributes'] == True and an error is "
    "raised while reading the attributes.",
    PydanticError.GREATER_THAN: "This error is raised when the value is not greater than the field's `gt` constraint.",
    PydanticError.GREATER_THAN_EQUAL: "This error is raised when the value is not greater than or equal to the field's `ge` "
    "constraint.",
    PydanticError.INT_FROM_FLOAT: "This error is raised when you provide a `float` value for an `int` field.",
    PydanticError.INT_PARSING: "This error is raised when the input value is a string that cannot be parsed as an integer.",
    PydanticError.INT_PARSING_SIZE: "This error is raised when the input value is a string that cannot be parsed as an integer "
    "because it is too large.",
    PydanticError.INT_TYPE: "This error is raised when the input value's type is not valid for an `int` field.",
    PydanticError.INVALID_KEY: "This error is raised when attempting to validate a `dict` that has a key that is not an "
    "instance of `str`.",
    PydanticError.IS_INSTANCE_OF: "This error is raised when the input value is not an instance of the expected type.",
    PydanticError.IS_SUBCLASS_OF: "This error is raised when the input value is not a subclass of the expected type.",
    PydanticError.ITERABLE_TYPE: "This error is raised when the input value's type is not valid for an iterable field.",
    PydanticError.ITERATION_ERROR: "This error is raised when an error occurs while iterating over the input value.",
    PydanticError.JSON_INVALID: "This error is raised when the input value is not valid JSON.",
    PydanticError.JSON_TYPE: "This error is raised when the input value's type is not valid for a JSON field.",
    PydanticError.LESS_THAN: "This error is raised when the value is not less than the field's `lt` constraint.",
    PydanticError.LESS_THAN_EQUAL: "This error is raised when the value is not less than or equal to the field's `le` "
    "constraint.",
    PydanticError.LIST_TYPE: "This error is raised when the input value's type is not valid for a `list` field.",
    PydanticError.LITERAL_ERROR: "This error is raised when the input value is not one of the expected literals.",
    PydanticError.MAPPING_TYPE: "This error is raised when the input value's type is not valid for a mapping field.",
    PydanticError.MISSING: "This error is raised when a required value is missing.",
    PydanticError.MISSING_ARGUMENT: "This error is raised when a required positional-or-keyword argument is not passed to a "
    "function decorated with `validate_call`.",
    PydanticError.MISSING_KEYWORD_ONLY_ARGUMENT: "This error is raised when a required keyword-only argument is not passed to a "
    "function decorated with `validate_call`.",
    PydanticError.MISSING_POSITIONAL_ONLY_ARGUMENT: "This error is raised when a required positional-only argument is not passed "
    "to a function decorated with `validate_call`.",
    PydanticError.MODEL_ATTRIBUTES_TYPE: "This error is raised when the input value is not a valid dictionary, model instance, "
    "or instance that fields can be extracted from.",
    PydanticError.MODEL_TYPE: "This error is raised when the input to a model is not an instance of the model or dict.",
    PydanticError.MULTIPLE_ARGUMENT_VALUES: "This error is raised when you provide multiple values for a single argument while "
    "calling a function decorated with `validate_call`.",
    PydanticError.MULTIPLE_OF: "This error is raised when the value is not a multiple of the field's `multiple_of` constraint.",
    PydanticError.NEEDS_PYTHON_OBJECT: "This type of error is raised when validation is attempted from a format that cannot be "
    "converted to a Python object. For example, we cannot check `isinstance` or `issubclass` "
    "from JSON.",
    PydanticError.NO_SUCH_ATTRIBUTE: "This error is raised when the input value does not have the expected attribute.",
    PydanticError.NONE_REQUIRED: "This error is raised when the input value is not `None` for a field that requires `None`.",
    PydanticError.RECURSION_LOOP: "This error is raised when a recursion loop is detected.",
    PydanticError.SET_TYPE: "This error is raised when the input value's type is not valid for a `set` field.",
    PydanticError.STRING_PATTERN_MISMATCH: "This error is raised when the input value doesn't match the field's `pattern` "
    "constraint.",
    PydanticError.STRING_SUB_TYPE: "This error is raised when the value is an instance of a strict subtype of `str` when the "
    "field is strict.",
    PydanticError.STRING_TOO_LONG: "This error is raised when the input value is a string whose length is greater than the "
    "field's `max_length` constraint.",
    PydanticError.STRING_TOO_SHORT: "This error is raised when the input value is a string whose length is less than the "
    "field's `min_length` constraint.",
    PydanticError.STRING_TYPE: "This error is raised when the input value's type is not valid for a `str` field.",
    PydanticError.STRING_UNICODE: "This error is raised when the value cannot be parsed as a Unicode string.",
    PydanticError.TIME_DELTA_PARSING: "This error is raised when the input value is a string that cannot be parsed for a "
    "`timedelta` field.",
    PydanticError.TIME_DELTA_TYPE: "This error is raised when the input value's type is not valid for a `timedelta` field.",
    PydanticError.TIME_PARSING: "This error is raised when the input value is a string that cannot be parsed for a `time` field.",
    PydanticError.TIME_TYPE: "This error is raised when the input value's type is not valid for a `time` field.",
    PydanticError.TIMEZONE_AWARE: "This error is raised when the `datetime` value provided for a timezone-aware `datetime` "
    "field doesn't have timezone information.",
    PydanticError.TIMEZONE_NAIVE: "This error is raised when the `datetime` value provided for a timezone-naive `datetime` "
    "field has timezone information.",
    PydanticError.TOO_LONG: "This error is raised when the value is longer than the field's `max_length` constraint.",
    PydanticError.TOO_SHORT: "This error is raised when the value is shorter than the field's `min_length` constraint.",
    PydanticError.TUPLE_TYPE: "This error is raised when the input value's type is not valid for a `tuple` field.",
    PydanticError.UNEXPECTED_KEYWORD_ARGUMENT: "This error is raised when an unexpected keyword argument is passed to a "
    "function decorated with `validate_arguments`.",
    PydanticError.UNEXPECTED_POSITIONAL_ARGUMENT: "This error is raised when an unexpected positional argument is passed to a "
    "function decorated with `validate_arguments`.",
    PydanticError.UNION_TAG_INVALID: "This error is raised when the input's discriminator is not one of the expected values.",
    PydanticError.UNION_TAG_NOT_FOUND: "This error is raised when it is not possible to extract a discriminator value from the "
    "input.",
    PydanticError.URL_PARSING: "This error is raised when the input value is a string that cannot be parsed as a URL.",
    PydanticError.URL_SCHEME: "This error is raised when the URL scheme is not valid for the URL type of the field.",
    PydanticError.URL_SYNTAX_VIOLATION: "This error is raised when the URL has a syntax violation.",
    PydanticError.URL_TOO_LONG: "This error is raised when the URL length is greater than 2083.",
    PydanticError.URL_TYPE: "This error is raised when the input value's type is not valid for a URL field.",
    PydanticError.UUID_PARSING: "This error is raised when the input value's type is not valid for a UUID field.",
    PydanticError.UUID_TYPE: "This error is raised when the input value's type is not valid instance for a UUID field (str, "
    "bytes or UUID).",
    PydanticError.UUID_VERSION: "This error is raised when the input value's type is not match UUID version.",
    PydanticError.VALUE_ERROR: "This error is raised when the input value is not valid.",
}
"""
All possible pydantic error types and their descriptions for creating error models for diagnostic schema.
"""

IGNORED_PYDANTIC_ERROR_TYPES: set[PydanticError] = {
    PydanticError.ARGUMENTS_TYPE,
    PydanticError.CALLABLE_TYPE,
    PydanticError.DATACLASS_EXACT_TYPE,
    PydanticError.DATACLASS_TYPE,
    PydanticError.DATETIME_OBJECT_INVALID,
    PydanticError.GET_ATTRIBUTE_ERROR,
    PydanticError.IS_INSTANCE_OF,
    PydanticError.IS_SUBCLASS_OF,
    PydanticError.MODEL_ATTRIBUTES_TYPE,
    PydanticError.MODEL_TYPE,
    PydanticError.NEEDS_PYTHON_OBJECT,
    PydanticError.MISSING_ARGUMENT,
    PydanticError.MISSING_KEYWORD_ONLY_ARGUMENT,
    PydanticError.MISSING_POSITIONAL_ONLY_ARGUMENT,
    PydanticError.MULTIPLE_ARGUMENT_VALUES,
    PydanticError.NO_SUCH_ATTRIBUTE,
    PydanticError.RECURSION_LOOP,
    PydanticError.UNEXPECTED_KEYWORD_ARGUMENT,
    PydanticError.UNEXPECTED_POSITIONAL_ARGUMENT,
}
"""
List of error types that are not included by default in the schema, only if explicitly requested.
"""

_MODEL_VALIDATION_SCHEMA_CACHE: dict[frozenset[str], Type[ModelValidationError]] = {}
_SCHEMA_CACHE: dict[frozenset[Any], Type[DiagnosticResponse[GenericError]]] = {}


def _pydantic_error_factory(include_pydantic_errors: Literal[True] | Collection[PydanticError | str]) -> Type[GenericError]:
    """
    Build a pydantic model describing all of specified pydantic error types.
    :param include_pydantic_errors: Specify error types
    """

    error_types: set[PydanticError] = (
        (set(ALL_PYDANTIC_ERROR_TYPES.keys()) - IGNORED_PYDANTIC_ERROR_TYPES)
        if include_pydantic_errors is True
        else {
            PydanticError(error_type) if not isinstance(error_type, PydanticError) else error_type
            for error_type in include_pydantic_errors
        }
    )

    cache_key = frozenset(error_types)
    if cache_key not in _MODEL_VALIDATION_SCHEMA_CACHE:
        error_desc = "\n".join(f" - `{error_type}`: {ALL_PYDANTIC_ERROR_TYPES[error_type]}" for error_type in error_types)

        _MODEL_VALIDATION_SCHEMA_CACHE[cache_key] = create_model(
            "ModelValidationError",
            __doc__=f"Model validation error. Possible types are:\n\n{error_desc}",
            __base__=ModelValidationError,
            type=(StrEnum("ErrorTypes", [(error_type.name, error_type.value) for error_type in error_types]), ...),
        )

    return _MODEL_VALIDATION_SCHEMA_CACHE[cache_key]


def _flatten_schema_int(schema: Any, defs: dict[str, Any], defs_prefix: str) -> Any:
    """
    Flatten model schema with $ref references, to be able to directly include in response schema without the need to
    populate global defs (which would produce duplicate models, which would be confusing).

    :param schema: Schema to flatten.
    :param defs: Definitions base dictionary.
    :param defs_prefix: Prefix to strip from $ref references to resolve definition in defs.
    :return: Flattened JSON schema without $refs.
    """

    if isinstance(schema, dict):
        if "$ref" in schema:
            ref = schema.pop("$ref")
            if ref.startswith(defs_prefix):
                ref = ref[len(defs_prefix) :]
                if ref in defs:
                    schema.update(defs[ref])
                else:
                    raise ValueError(f"Unable to resolve reference: {ref}")
            else:
                raise ValueError(f"Unable to resolve reference: {ref}")

        return {key: _flatten_schema_int(value, defs, defs_prefix) for key, value in schema.items()}

    if isinstance(schema, list):
        return [_flatten_schema_int(item, defs, defs_prefix) for item in schema]

    return schema


_DEFS_PREFIX = "#/$defs/"


def _flatten_schema(model: Type[BaseModel]) -> dict[str, Any]:
    """
    Return model schema without $refs, to be able to directly include in response schema without the need to populate
    global defs (which would produce duplicate models, which would be confusing).

    :param model: Model to generate schema for.
    :return: Flattened JSON schema without $refs.
    """
    schema = model.model_json_schema(by_alias=True, ref_template=f"{_DEFS_PREFIX}{{model}}")
    if "$defs" in schema:
        defs = schema.pop("$defs")
        return _flatten_schema_int(schema, defs, _DEFS_PREFIX)

    return schema


def diagnostic_schema(
    types: Optional[Collection[Type[DiagnosticError]]] = None,
    include_pydantic_errors: bool | Collection[PydanticError | str] = True,
) -> dict[int | str, dict[str, Any]]:
    """
    Create a diagnostic response schema for the given error types. Usefull for documenting
    API endpoint diagnostic responses for OpenAPI schema.

    Usage with FastAPI:

    >>> from fastapi import FastAPI
    >>> from szn_sklik_dialoc.models import diagnostic_schema
    >>> from szn_sklik_dialoc.errors import EntityNotFound, EntityAlreadyExists
    >>>
    >>> app = FastAPI()
    >>>
    >>>
    >>> @app.get("/", responses=diagnostic_schema([EntityNotFound, EntityAlreadyExists]))
    >>> async def index():
    >>>     pass

    :param types: Collection of diagnostic error types for which the response schema should be generated.
    :param include_pydantic_errors: Include pydantic's default error schema for 422.
       If True, include all pydantic error types. If False, does not include any. If a collection of strings,
       only specified error types will be included.
    :return: Diagnostic response schema suitable for FastAPI endpoint.
    """
    if not types:
        types = []

    errors_by_status: dict[int, list[Type[GenericError]]] = {}

    if include_pydantic_errors:
        pydantic_model = _pydantic_error_factory(include_pydantic_errors)
        errors_by_status[HTTPStatus.UNPROCESSABLE_ENTITY] = [pydantic_model]

    # Group errors by status code.
    for t in types:
        errors_by_status.setdefault(t.status_code, []).append(t)

    # Create schema for each status code.
    out: dict[int | str, dict[str, Any]] = {}

    for status, errors in errors_by_status.items():
        out[int(status)] = {
            "description": f"Diagnostic response for HTTP status {status}.",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "type": "array",
                                "items": {"oneOf": [_flatten_schema(error) for error in errors]},
                            }
                        },
                    },
                },
            },
        }

    return out
