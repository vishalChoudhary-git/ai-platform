from fastapi import Header, HTTPException, status

from .models import AuthenticatedUser


async def get_debug_user(
    role: str | None = Header(default=None, alias="X-Debug-User-Role"),
    email: str = Header(default="developer@example.com", alias="X-Debug-User-Email"),
) -> AuthenticatedUser:
    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Debug-User-Role.",
        )
    return AuthenticatedUser(email=email, roles=frozenset({role.upper()}))
