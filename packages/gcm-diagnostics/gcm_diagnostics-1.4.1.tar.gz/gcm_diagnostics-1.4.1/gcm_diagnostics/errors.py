from __future__ import annotations

from http import HTTPStatus
from typing import Any

from .models import DiagnosticError


class EntityNotFound(DiagnosticError):
    """
    Diagnostic error when requested entity was not found.
    """

    status_code = HTTPStatus.NOT_FOUND

    type: str = "entity_not_found"
    msg: str = "Entity does not exists."
    id: Any


class EntityAlreadyExists(DiagnosticError):
    """
    Diagnostic error when requested entity is already present. This is usually thrown when trying to create duplicate.
    """

    status_code = HTTPStatus.CONFLICT

    type: str = "entity_already_exists"
    msg: str = "Entity already exists."
    entity: Any


class InvalidValue(DiagnosticError):
    """
    Value of attribute is not valid according to validation rules.
    """

    type: str = "invalid_value"
    msg: str = "Invalid field value"
    expected: Any = None
    real: Any = None


class LogicError(DiagnosticError):
    """
    Logic error, trying to do something that is not allowed right now.
    """

    type: str = "logic_error"
    msg: str = "Logical error"


class Forbidden(DiagnosticError):
    """
    Access denied error.
    """

    status_code = HTTPStatus.FORBIDDEN

    type: str = "forbidden"
    msg: str = "Forbidden"


class Missing(DiagnosticError):
    """
    Missing required field.
    """

    type: str = "missing"
    msg: str = "Field required"
