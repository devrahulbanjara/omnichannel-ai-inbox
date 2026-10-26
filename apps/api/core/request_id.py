"""Middleware: give every request an id, attach it to every log line, and log how it went."""

import time
import uuid

from fastapi import Request, Response
from loguru import logger

HEADER = "X-Request-ID"


async def request_id_middleware(request: Request, call_next) -> Response:
    # Reuse the caller's id if it sent a sane one (lets us follow a request across services).
    incoming = request.headers.get(HEADER, "")
    request_id = incoming if 0 < len(incoming) <= 64 else uuid.uuid4().hex

    # Every log line written while handling this request gets this request_id.
    with logger.contextualize(request_id=request_id):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("{} {} crashed", request.method, request.url.path)
            raise
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
