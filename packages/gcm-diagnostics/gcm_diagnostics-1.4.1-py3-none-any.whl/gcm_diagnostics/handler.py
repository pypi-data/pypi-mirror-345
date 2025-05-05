from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .exception import DiagnosticException


def handle_diagnostic_error(request: Request, exc: Exception) -> Response:
    # pylint: disable=unused-argument
    """
    FastAPI error handler that catches DiagnosticException and formats response acordingly.

    Usage:
    >>> app: FastAPI = ...
    >>> app.add_exception_handler(DiagnosticException, handle_diagnostic_error)
    """

    if not isinstance(exc, DiagnosticException):
        raise TypeError(
            "handle_diagnostic_error can be used only to handle DiagnosticException instances, instead, got"
            f"called for instance of type: {type(exc)}"
        )

    return Response(content=exc.response.model_dump_json(), status_code=exc.status_code, media_type=JSONResponse.media_type)


def install_exception_handler(app: FastAPI) -> None:
    """
    Install diagnostic exception handler to FastAPI application.
    :param app: FastAPI instance where to install the handler.
    """
    app.add_exception_handler(DiagnosticException, handle_diagnostic_error)
