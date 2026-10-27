"""Exception handlers. Every error response is an ErrorResponse: {"error": {"code", "message"}}."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.exceptions import AppError
from app.schemas.error import ErrorBody, ErrorResponse, FieldError


def error_response(
    status: int, code: str, message: str, details: list[FieldError] | None = None
) -> JSONResponse:
    body = ErrorResponse(error=ErrorBody(code=code, message=message, details=details))
    return JSONResponse(status_code=status, content=body.model_dump(exclude_none=True))


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    return error_response(exc.status_code, exc.code, exc.message)


async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    code = HTTPStatus(exc.status_code).phrase.lower().replace(" ", "_")  # 404 -> "not_found"
    return error_response(exc.status_code, code, str(exc.detail))


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for err in exc.errors():
        parts = []
        for part in err["loc"]:  # e.g. ("body", "text") -> "body.text"
            parts.append(str(part))
        details.append(FieldError(field=".".join(parts), message=err["msg"]))
    return error_response(422, "validation_error", "The request is not valid", details=details)


def internal_error_response() -> JSONResponse:
    """Generic 500 response. Exception details are logged, never returned."""
    return error_response(500, "internal_error", "Something went wrong on our side")


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    return internal_error_response()


def add_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(HTTPException, handle_http_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
