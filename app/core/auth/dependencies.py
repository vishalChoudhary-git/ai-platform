from fastapi import Depends, HTTPException, status

from .debug import get_debug_user
from .models import AuthenticatedUser


async def get_current_user(
    user: AuthenticatedUser = Depends(get_debug_user),
) -> AuthenticatedUser:
    return user


def require_role(role: str):
    async def dependency(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if role.upper() not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' is required.",
            )
        return user

    return dependency
