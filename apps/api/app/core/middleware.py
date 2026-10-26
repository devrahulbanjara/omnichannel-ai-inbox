"""Request ID middleware: assigns an ID per request, binds it to log records, logs each request."""

import time
import uuid

from fastapi import Request, Response
from loguru import logger

from app.core.errors import internal_error_response

HEADER = "X-Request-ID"


async def request_id_middleware(request: Request, call_next) -> Response:
    # Accept a client-supplied ID of up to 64 characters; otherwise generate one.
    incoming = request.headers.get(HEADER, "")
    request_id = incoming if 0 < len(incoming) <= 64 else uuid.uuid4().hex

    with logger.contextualize(request_id=request_id):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("{} {} crashed", request.method, request.url.path)
            response = internal_error_response()
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "{} {} → {} ({:.1f} ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

    response.headers[HEADER] = request_id
    return response
