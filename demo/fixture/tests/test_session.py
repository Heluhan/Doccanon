"""Session recovery behavior."""

from auth.session import recover_session


class MemoryStore:
    def __init__(self, records=None):
        self.records = records or {}

    def load(self, user_id):
        return self.records.get(user_id)


def test_restores_saved_state():
    store = MemoryStore({"u1": {"user_id": "u1", "state": {"step": 3}}})
    assert recover_session(store, "u1").state == {"step": 3}


def test_rejects_foreign_state():
    store = MemoryStore({"u1": {"user_id": "u2", "state": {"step": 9}}})
    assert recover_session(store, "u1").state == {}
