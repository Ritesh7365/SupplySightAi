"""Assign a unique request ID to every inbound HTTP request."""

from __future__ import annotations

import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Ensure every request has a correlation ID.

    Accepts an inbound ``X-Request-ID`` when present; otherwise generates a UUID4.
    Stores the value on ``request.state.request_id`` and echoes it on the response.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        incoming = request.headers.get(REQUEST_ID_HEADER)
        request_id = (incoming or "").strip() or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
