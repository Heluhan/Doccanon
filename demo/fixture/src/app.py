"""Application entry point."""

from auth.session import recover_session, new_session


def resume(store, user_id: str):
    session = recover_session(store, user_id)
    if not session.state:
        session = new_session(user_id)
    return session
