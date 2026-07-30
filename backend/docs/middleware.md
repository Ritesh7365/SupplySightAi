# Middleware — SupplySight AI

Middleware is registered in `backend.app.main.create_app`. Starlette runs
middleware in **reverse registration order** on the inbound path.

## Stack (inbound order)

1. **RequestIdMiddleware** — correlation ID  
2. **RequestTimingMiddleware** — duration + access log  
3. **ResponseHeadersMiddleware** — standard headers  
4. **CORSMiddleware** — configurable origins  
5. **GZipMiddleware** — compress bodies ≥ 1000 bytes  
6. Route handlers / exception handlers  

## RequestIdMiddleware

**Module:** `backend.app.middleware.request_id`

- Reads inbound `X-Request-ID` or generates UUID4
- Stores on `request.state.request_id`
- Echoes `X-Request-ID` on the response
- Included in error JSON (`request_id`) and access logs

## RequestTimingMiddleware

**Module:** `backend.app.middleware.request_timing`

Logs one line per request:

```
request_id=… method=GET path=/api/v1/dashboard/executive duration_ms=12.34 status=200 client_ip=127.0.0.1
```

Also sets `X-Process-Time-Ms`.

Client IP prefers `X-Forwarded-For` (first hop) when present.

## ResponseHeadersMiddleware

**Module:** `backend.app.middleware.response_headers`

Sets (via `setdefault`, so handlers may override):

| Header | Value |
|--------|--------|
| `X-API-Version` | Package version |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `no-referrer` |
| `Cache-Control` | `no-store` |

## GZipMiddleware

Starlette `GZipMiddleware` with `minimum_size=1000`.

Clients must send `Accept-Encoding: gzip` to receive compressed payloads.

## CORSMiddleware

Origins from `Settings.cors_origins` / `CORS_ORIGINS`.

Exposes `X-Request-ID`, `X-Process-Time-Ms`, and `X-API-Version` to browsers.

## Exception interaction

Global handlers in `backend.app.core.exceptions` run after routing failures.
They attach the same `request_id` when available. Timing middleware still logs
duration for successful responses; unhandled exceptions are logged with
`status=500` before re-raise / handler response.
