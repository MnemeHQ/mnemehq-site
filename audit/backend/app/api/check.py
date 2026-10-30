"""Stateless ADR check for the free ADR checker page.

POST only: there is no listing or lookup route, because nothing is kept.
The request body is never logged; the log line carries kind, size bucket,
status and duration.
"""
from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque

from fastapi import APIRouter, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from app.services.adr_check import (
    MAX_TEXT_BYTES,
    CheckInputError,
    check_adr,
    size_bucket,
    validate_text,
)

logger = logging.getLogger("app.check")

router = APIRouter(prefix="/api/v1", tags=["check"])

# JSON envelope on top of the 64 KB text limit (escaping can grow the body).
MAX_BODY_BYTES = 2 * MAX_TEXT_BYTES + 1024

# In-process limits. Adequate while the service runs a single instance;
# they keep a burst of checks from slowing the Audit on the same instance.
PER_CLIENT_LIMIT = 20
GLOBAL_LIMIT = 120
WINDOW_SECONDS = 60.0


class RateLimiter:
    def __init__(self, per_client: int, total: int, window: float):
        self.per_client, self.total, self.window = per_client, total, window
        self._lock = threading.Lock()
        self._clients: dict[str, deque] = {}
        self._all: deque = deque()

    def allow(self, client: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        cutoff = now - self.window
        with self._lock:
            while self._all and self._all[0] <= cutoff:
                self._all.popleft()
            hits = self._clients.setdefault(client, deque())
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.per_client or len(self._all) >= self.total:
                return False
            hits.append(now)
            self._all.append(now)
            if len(self._clients) > 10_000:
                self._clients = {k: v for k, v in self._clients.items() if v}
            return True

    def reset(self) -> None:
        with self._lock:
            self._clients.clear()
            self._all.clear()


limiter = RateLimiter(PER_CLIENT_LIMIT, GLOBAL_LIMIT, WINDOW_SECONDS)


def client_key(request: Request) -> str:
    # Cloud Run appends the connecting client's address as the last
    # X-Forwarded-For entry; earlier entries are caller-supplied.
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded.strip():
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def _log(status: int, started: float, bucket: str = "none") -> None:
    logger.info(
        "check kind=adr size_bucket=%s status=%d duration_ms=%d",
        bucket, status, int((time.monotonic() - started) * 1000),
    )


@router.post("/check")
async def check(request: Request):
    started = time.monotonic()
    if not limiter.allow(client_key(request)):
        _log(429, started)
        raise HTTPException(429, "Too many checks. Wait a minute and try again.")

    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        _log(413, started)
        raise HTTPException(413, "The ADR is over the 64 KB limit.")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        _log(400, started)
        raise HTTPException(400, "Send JSON with the ADR text as UTF-8.")
    if not isinstance(payload, dict) or payload.get("kind", "adr") != "adr":
        _log(400, started)
        raise HTTPException(400, "Only ADR checks are supported.")

    try:
        text = validate_text(payload.get("text"))
    except CheckInputError as exc:
        status = 413 if exc.code == "too_large" else 422
        _log(status, started)
        raise HTTPException(status, str(exc))

    bucket = size_bucket(text)
    try:
        result = await run_in_threadpool(check_adr, text)
    except Exception as exc:
        # Exception messages from parsers can quote the input, so only the
        # type name is logged, with no traceback.
        logger.warning("check kind=adr failed error_type=%s", type(exc).__name__)
        _log(422, started, bucket)
        raise HTTPException(422, "This ADR could not be read. Check its formatting and try again.")
    _log(200, started, bucket)
    return {"success": True, **result.to_dict()}
