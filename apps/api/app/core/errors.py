"""Exception handlers. Every error response has the shape {"error": {"code", "message"}}."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.exceptions import AppError


def error_response(status: int, code: str, message: str, **extra) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, **extra}},
    )


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    return error_response(exc.status_code, exc.code, exc.message)


async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    code = HTTPStatus(exc.status_code).phrase.lower().replace(" ", "_")  # 404 -> "not_found"
    return error_response(exc.status_code, code, str(exc.detail))


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {"field": ".".join(str(part) for part in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return error_response(422, "validation_error", "The request is not valid", details=details)


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Generic 500 response. Exception details are logged, never returned."""
    return error_response(500, "internal_error", "Something went wrong on our side")


def add_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(HTTPException, handle_http_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
