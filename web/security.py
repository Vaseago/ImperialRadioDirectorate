"""
web/security.py

CSRF mitigation for this app's no-body state-changing POST route
(/api/library/rescan). Direct port of the sibling apps' identical fix -
see any of their web/security.py modules for the full reasoning. NOT a
real anti-forgery token (nothing secret or per-session) - deliberately
doesn't need to be, since the goal is only to rule out a bare HTML form,
not to authenticate the caller (this app has no concept of authenticated
callers at all - see docs/SECURITY_MODEL.md).
"""

from fastapi import Header, HTTPException

REQUIRED_HEADER_NAME = "X-IRD-Request"
REQUIRED_HEADER_VALUE = "1"


def require_same_origin_header(x_ird_request: str | None = Header(default=None)) -> None:
    if x_ird_request != REQUIRED_HEADER_VALUE:
        raise HTTPException(
            status_code=403,
            detail=f"Missing or invalid {REQUIRED_HEADER_NAME} header - this endpoint only accepts requests from this app's own frontend.",
        )
