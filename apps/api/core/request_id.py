"""Middleware: give every request an id, return it in a header, and log how the request went."""

import logging
import time
import uuid

from fastapi import Request, Response

from core.logs import request_id_var

log = logging.getLogger("api.request")

HEADER = "X-Request-ID"


async def request_id_middleware(request: Request, call_next) -> Response:
    # Reuse the caller's id if it sent a sane one (lets us follow a request across services).
    incoming = request.headers.get(HEADER, "")
    request_id = incoming if 0 < len(incoming) <= 64 else uuid.uuid4().hex
    request_id_var.set(request_id)

    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers[HEADER] = request_id
        return response
    except Exception:
        log.exception("unhandled error")
        raise
    finally:
        log.info(
            "request finished",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": status,
                "duration_ms": round((time.perf_counter() - start) * 1000, 1),
            },
        )
