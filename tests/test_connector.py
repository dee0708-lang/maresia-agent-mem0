import os
import unittest
from unittest.mock import patch
from connector import Mem0Profiles


class ConnectorTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        def execute(tool, arguments):
            self.calls.append((tool, arguments))
            return {"status": "queued", "synthetic": True}
        self.execute = execute

    def test_disabled_by_default(self):
        with self.assertRaises(RuntimeError):
            Mem0Profiles(self.execute, "synthetic-user").search("test")
        self.assertEqual(self.calls, [])

    def test_user_is_required(self):
        for value in ("", "   ", None):
            with self.assertRaises(ValueError):
                Mem0Profiles(self.execute, value)

    def test_search_is_user_bound(self):
        Mem0Profiles(self.execute, "synthetic-user", enabled=True).search("test", limit=3)
        tool, args = self.calls[0]
        self.assertEqual(tool, "MEM0_PERFORM_SEMANTIC_SEARCH_ON_MEMORIES")
        self.assertEqual(args["user_id"], "synthetic-user")
        self.assertTrue(args["filter_memories"])
        self.assertEqual(args["top_k"], 3)

    def test_write_flag_and_consent(self):
        for allow, consent in ((False, True), (True, False)):
            with self.assertRaises(PermissionError):
                Mem0Profiles(self.execute, "synthetic-user", enabled=True,
                    allow_writes=allow).remember("Synthetic fact", consent_confirmed=consent)
        self.assertEqual(self.calls, [])

    def test_remember_is_verbatim_and_user_bound(self):
        result = Mem0Profiles(self.execute, "synthetic-user", enabled=True,
            allow_writes=True).remember("Synthetic fact", consent_confirmed=True)
        tool, args = self.calls[0]
        self.assertEqual(tool, "MEM0_ADD_NEW_MEMORY_RECORDS")
        self.assertEqual(args["user_id"], "synthetic-user")
        self.assertFalse(args["infer"])
        self.assertTrue(args["async_mode"])
        self.assertEqual(args["messages"], [{"role": "user", "content": "Synthetic fact"}])
        self.assertEqual(result["status"], "queued")

    def test_limits(self):
        with self.assertRaises(ValueError):
            Mem0Profiles(self.execute, "synthetic-user", enabled=True).search("test", limit=True)
        self.assertEqual(self.calls, [])

    def test_blank_content(self):
        with self.assertRaises(ValueError):
            Mem0Profiles(self.execute, "synthetic-user", enabled=True,
                allow_writes=True).remember(" ", consent_confirmed=True)
        self.assertEqual(self.calls, [])

    def test_environment_defaults_off(self):
        with patch.dict(os.environ, {}, clear=True):
            connector = Mem0Profiles.from_env(self.execute, "synthetic-user")
            self.assertFalse(connector.enabled or connector.allow_writes)
