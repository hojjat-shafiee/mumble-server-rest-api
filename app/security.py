from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_auth = HTTPBearer(auto_error=False)


def verify_api_key(
    header_key: Optional[str] = Security(api_key_header),
    bearer_creds: Optional[HTTPAuthorizationCredentials] = Security(bearer_auth),
) -> bool:
    """
    Enforces API key authentication if API_KEY is configured in settings.
    Accepts keys via either 'X-API-Key' header or 'Authorization: Bearer <key>'.
    If API_KEY is empty/unset, authentication is bypassed.
    """
    if not settings.API_KEY:
        return True

    provided_key = header_key or (bearer_creds.credentials if bearer_creds else None)

    if not provided_key or provided_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key. Provide via 'X-API-Key' header or 'Authorization: Bearer <key>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True

