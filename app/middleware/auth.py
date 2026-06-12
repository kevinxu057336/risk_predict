import os
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

API_KEY = os.getenv("RISK_API_KEY", "")
API_KEY_HEADER = "X-API-Key"

PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}
WRITE_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not API_KEY:
            return await call_next(request)

        path = request.url.path
        if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        if request.method in WRITE_METHODS:
            key = request.headers.get(API_KEY_HEADER, "")
            if key != API_KEY:
                return JSONResponse(status_code=401, content={"detail": "Invalid or missing API Key"})

        return await call_next(request)
