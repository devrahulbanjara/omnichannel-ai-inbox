from typing import Annotated, Any

from pydantic import BaseModel, Field


class FieldError(BaseModel):
    field: Annotated[str, Field(description="Path to the bad input, e.g. body.text")]
    message: str


class ErrorBody(BaseModel):
    code: Annotated[str, Field(description="Stable machine-readable code, e.g. not_found")]
    message: Annotated[str, Field(description="Human-readable explanation")]
    details: Annotated[
        list[FieldError] | None, Field(description="Per-field problems; only on validation_error")
    ] = None


class ErrorResponse(BaseModel):
    """Shape of every error response."""

    error: ErrorBody


# For APIRouter(responses=...): documents the error shape in the OpenAPI schema.
ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Not found"},
    422: {"model": ErrorResponse, "description": "The request is not valid"},
    500: {"model": ErrorResponse, "description": "Unexpected server error"},
}
