"""Access token minting and validation."""

import secrets


def issue_token(user_id: str) -> str:
    return f"{user_id}.{secrets.token_urlsafe(16)}"


def token_owner(token: str) -> str:
    return token.split(".", 1)[0]
