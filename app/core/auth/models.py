from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedUser:
    email: str
    roles: frozenset[str]
