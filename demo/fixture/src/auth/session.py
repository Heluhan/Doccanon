"""Session recovery for authenticated users."""

from dataclasses import dataclass, field


@dataclass
class Session:
    user_id: str
    state: dict = field(default_factory=dict)


def recover_session(store, user_id: str) -> Session:
    """Restore the current user's saved session or start a clean one."""
    record = store.load(user_id)
    if not record or record.get("user_id") != user_id:
        return Session(user_id=user_id)
    return Session(user_id=user_id, state=dict(record["state"]))


def new_session(user_id: str) -> Session:
    return Session(user_id=user_id)
