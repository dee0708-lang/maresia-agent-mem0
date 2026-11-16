"""User-bound Mem0 profile adapter. No credentials, persistence, or background jobs."""
import os


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string.")
    return value


class Mem0Profiles:
    def __init__(self, execute, user_id, *, enabled=False, allow_writes=False):
        self.user_id = text(user_id, "user_id")
        self.execute = execute
        self.enabled, self.allow_writes = enabled is True, allow_writes is True

    @classmethod
    def from_env(cls, execute, user_id):
        return cls(execute, user_id,
                   enabled=os.getenv("MARESIA_ENABLE_LIVE_SYNC", "false").lower() == "true",
                   allow_writes=os.getenv("MARESIA_ALLOW_WRITES", "false").lower() == "true")

    def _live(self):
        if not self.enabled:
            raise RuntimeError("Live access is disabled.")

    def search(self, query, *, limit=10):
        self._live()
        text(query, "query")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer from 1 to 100.")
        return self.execute("MEM0_PERFORM_SEMANTIC_SEARCH_ON_MEMORIES", {
            "query": query, "user_id": self.user_id, "top_k": limit,
            "filter_memories": True,
        })

    def remember(self, content, *, consent_confirmed=False):
        self._live()
        if not self.allow_writes or consent_confirmed is not True:
            raise PermissionError("Profile writes require explicit opt-in and confirmed consent.")
        text(content, "content")
        return self.execute("MEM0_ADD_NEW_MEMORY_RECORDS", {
            "messages": [{"role": "user", "content": content}],
            "user_id": self.user_id, "infer": False,
            "async_mode": True, "output_format": "v1.1",
        })
