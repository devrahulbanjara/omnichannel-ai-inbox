"""Every error leaves the API in the same shape: {"error": {"code": ..., "message": ...}}."""

from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException


def error_response(status: int, code: str, message: str, **extra) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, **extra}},
    )


async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    """Errors we raise on purpose (404, 401…) and unknown URLs."""
    code = HTTPStatus(exc.status_code).phrase.lower().replace(" ", "_")  # 404 → "not_found"
    return error_response(exc.status_code, code, str(exc.detail))


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """The request didn't match our Pydantic models (422)."""
    details = [
        {"field": ".".join(str(part) for part in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return error_response(422, "validation_error", "The request is not valid", details=details)


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """A bug. Never show internal details to the caller; the logs have them."""
    return error_response(500, "internal_error", "Something went wrong on our side")


def add_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, handle_http_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
