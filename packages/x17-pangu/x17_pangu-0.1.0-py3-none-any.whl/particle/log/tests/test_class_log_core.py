import unittest
import time
from pangu.particle.log.log_core import LogCore
from pangu.particle.log.log_event import LogEvent


class TestLogCore(unittest.TestCase):

    def test_initialization(self):
        core = LogCore(name="central")
        self.assertIn("central", core.name)
        self.assertIsInstance(core.queue, type(__import__("queue").Queue()))
        self.assertTrue(core.id)

    def test_push_and_export_single(self):
        core = LogCore(name="unit")
        event = LogEvent(message="testing core log", level="info")
        core.push("platform", "auth", event)
        time.sleep(0.1)
        export = core.export("platform", "auth")
        self.assertEqual(len(export), 1)
        self.assertEqual(export[0]["message"], "testing core log")

    def test_export_by_group_only(self):
        core = LogCore(name="exportgroup")
        core.push("api", "login", LogEvent(message="login ok", level="info"))
        core.push("api", "logout", LogEvent(message="logout ok", level="info"))
        time.sleep(0.1)
        export = core.export("api")
        self.assertIn("login", export)
        self.assertIn("logout", export)

    def test_export_all(self):
        core = LogCore(name="alltest")
        core.push("system", "kernel", LogEvent(message="booting", level="info"))
        core.push("system", "kernel", LogEvent(message="running", level="debug"))
        core.push("system", "net", LogEvent(message="network online", level="info"))
        time.sleep(0.1)
        all_export = core.export()
        self.assertIn("system", all_export)
        self.assertIn("kernel", all_export["system"])
        self.assertIn("net", all_export["system"])
        self.assertEqual(len(all_export["system"]["kernel"]), 2)


if __name__ == "__main__":
    unittest.main()
