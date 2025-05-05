from __future__ import annotations

import logging
import operator
from typing import Generic, Optional, Sequence, TypeVar

from fastapi.exceptions import RequestValidationError

from .models import DiagnosticError, DiagnosticResponse

T = TypeVar("T", bound=DiagnosticError)


class DiagnosticException(RequestValidationError, Generic[T]):
    """
    Exception thrown when DiagnosticCollector collects any error. Contains all the collected errors, which
    then can be presented to user.
    """

    def __init__(self, detail: Optional[Sequence[T]] = None, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(detail or [])
        self.logger = logger or logging.root

    def errors(self) -> Sequence[T]:
        """
        Return all collected errors.
        """
        return super().errors()

    @property
    def status_code(self) -> int:
        """
        Return combined HTTP status code of the errors. If there are only errors of one type, return that
        error type's status code. Otherwise, returns generic 422 (Unprocessable entity) error.
        :return:
        """
        status_codes: set[int] = set()

        for error in self.errors():
            # The protected member here is intentional to not propagate it to OpenAPI schema (as it is not part
            # of the JSON response).
            status_codes.add(error.status_code)

        # If there is only one status code in all errors, return it.
        if len(status_codes) == 1:
            return status_codes.pop()

        # Decide which status code to return based on the highest 100th of the status codes.
        max_status_code_family = max(status_codes) // 100 * 100

        # Otherwise, return generic 422 status code.
        self.logger.debug(
            "Multiple error types detected (%r), returning aggregated %d status code", status_codes, max_status_code_family
        )

        return max_status_code_family

    @property
    def response(self) -> DiagnosticResponse[T]:
        """
        Create response model that represents the error. It has the same format as built-in FastAPIs
        RequestValidationError to provide uniform error reporting both from OpenAPI validations and
        also from business logic validations.
        """
        return DiagnosticResponse(
            detail=sorted(self.errors(), key=operator.attrgetter("loc")),
        )

    def __str__(self) -> str:
        return "Diagnostics:\n" + "\n".join(f"  - {error!s}" for error in self.errors())
