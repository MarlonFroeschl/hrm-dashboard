import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.security import decode_token

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Validate JWT bearer token and return the subject (user id / email)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except JWTError:
        logger.warning("JWT validation failed")
        raise credentials_exception

    sub: str | None = payload.get("sub")
    if sub is None:
        logger.warning("JWT payload missing 'sub' claim")
        raise credentials_exception

    return sub
