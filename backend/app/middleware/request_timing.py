"""Measure request duration and emit structured access logs."""

from __future__ import annotations

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("middleware.timing")

PROCESS_TIME_HEADER = "X-Process-Time-Ms"


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Time each request and log:

    Request ID · Method · Path · Execution Time · Status Code · Client IP
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        started = time.perf_counter()
        request_id = getattr(request.state, "request_id", "-")
        client_ip = _client_ip(request)

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            logger.exception(
                "request_id=%s method=%s path=%s duration_ms=%.2f status=%s client_ip=%s",
                request_id,
                request.method,
                request.url.path,
                elapsed_ms,
                500,
                client_ip,
            )
            raise

        elapsed_ms = (time.perf_counter() - started) * 1000.0
        response.headers[PROCESS_TIME_HEADER] = f"{elapsed_ms:.2f}"

        logger.info(
            "request_id=%s method=%s path=%s duration_ms=%.2f status=%s client_ip=%s",
            request_id,
            request.method,
            request.url.path,
            elapsed_ms,
            response.status_code,
            client_ip,
        )
        return response
