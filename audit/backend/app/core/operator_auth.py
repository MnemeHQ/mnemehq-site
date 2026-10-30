"""
Operator-only access for endpoints that list or change data across projects.

The visitor flow reaches audits and projects only through their own
unguessable ids (capability URLs). Endpoints that enumerate every project,
change a project, or expose contacts are for Mneme HQ operators, as
security/data-handling states ("accessible only to Mneme HQ operators").

The check fails closed: with MNEME_AUDIT_OPERATOR_TOKEN unset, every
operator endpoint answers 403. The token is read per request, so rotating
the Cloud Run secret needs no code change.
"""
from __future__ import annotations

import hmac
import os
from typing import Optional

from fastapi import Header, HTTPException, status

TOKEN_ENV = "MNEME_AUDIT_OPERATOR_TOKEN"


def require_operator(authorization: Optional[str] = Header(default=None)) -> None:
    expected = os.environ.get(TOKEN_ENV, "")
    if not expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Operator endpoints are disabled")
    scheme, _, supplied = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not hmac.compare_digest(supplied.encode(), expected.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Operator token required",
                            headers={"WWW-Authenticate": "Bearer"})
