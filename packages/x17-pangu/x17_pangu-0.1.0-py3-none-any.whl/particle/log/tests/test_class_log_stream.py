import unittest
from pangu.particle.log.log_event import LogEvent


class TestLogEvent(unittest.TestCase):

    def test_creation(self):
        event = LogEvent(message="System started", name="init", level="info")
        self.assertIsInstance(event.id, str)
        self.assertEqual(event.message, "System started")
        self.assertEqual(event.level, "INFO")
        self.assertIn("init", event.name)
        self.assertIsNotNone(event.datestamp)

    def test_repr_str(self):
        event = LogEvent(message="Hello", name="check")
        self.assertIsInstance(repr(event), str)
        self.assertIsInstance(str(event), str)
        self.assertIn("LogEvent(", repr(event))
        self.assertIn("LogEvent(", str(event))

    def test_dict_export(self):
        event = LogEvent(message="Export test", name="exporter", level="warning")
        d = event.dict
        self.assertIsInstance(d, dict)
        self.assertEqual(d["level"], "WARNING")
        self.assertEqual(d["message"], "Export test")
        self.assertIn("exporter", d["name"])
        self.assertEqual(event.export(), d)

    def test_from_dict(self):
        input_dict = {
            "message": "Loaded from dict",
            "level": "debug",
            "datestamp": "2025-04-01 12:00:00",
        }
        base = LogEvent("fallback")
        event = base.from_dict(input_dict)
        self.assertIsInstance(event, LogEvent)
        self.assertEqual(event.message, "Loaded from dict")
        self.assertEqual(event.level, "DEBUG")
        self.assertEqual(event.datestamp, "2025-04-01 12:00:00")


if __name__ == "__main__":
    unittest.main()
