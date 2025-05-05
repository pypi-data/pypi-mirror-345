import unittest
import time
from pangu.particle.log.log_core import LogCore
from pangu.particle.log.log_group import LogGroup
from pangu.particle.log.log_stream import LogStream
from pangu.particle.log.log_event import LogEvent


class TestLogSystemIntegration(unittest.TestCase):
    """
    Test the integration of the logging system with core, groups, and streams.
    This test verifies that the logging system can handle multiple streams
    and groups, and that events are correctly logged and exported.

    Args:
        unittest.TestCase: Inherits from the unittest TestCase class.

    """

    def test_stream_alone_logging(self):
        stream = LogStream(name="standalone")
        stream.info("Running alone")
        stream.warn("Alone warning")
        stream.error("Alone error")
        stream.debug("Alone debug")

    def test_stream_to_group(self):
        group = LogGroup(name="group1")
        stream = LogStream(name="api-auth")
        group.register_stream(stream)

        stream.info("Login started")
        stream.error("Invalid credentials")

        time.sleep(0.1)
        result = group.export()
        self.assertIn("api-auth", result)
        self.assertEqual(result["api-auth"][0]["message"], "Login started")
        self.assertEqual(result["api-auth"][1]["level"], "ERROR")

    def test_stream_to_group_to_core(self):
        core = LogCore(name="central")
        group = LogGroup(name="analytics", core=core)
        stream = LogStream(name="track")
        group.register_stream(stream)

        stream.info("Tracking page view")
        stream.warn("Slow analytics response")

        time.sleep(0.1)
        export = core.export(group.name, "track")
        self.assertEqual(len(export), 2)
        self.assertEqual(export[0]["message"], "Tracking page view")
        self.assertEqual(export[1]["level"], "WARNING")

    def test_multiple_streams_and_groups(self):
        core = LogCore(name="core")
        group1 = LogGroup(name="web", core=core)
        group2 = LogGroup(name="worker", core=core)

        s1 = LogStream(name="frontend")
        s2 = LogStream(name="backend")
        s3 = LogStream(name="job-runner")

        group1.register_stream(s1)
        group1.register_stream(s2)
        group2.register_stream(s3)

        s1.info("Page loaded")
        s2.error("API timeout")
        s3.debug("Job started")

        time.sleep(0.2)
        export = core.export()
        self.assertIn("web", export)
        self.assertIn("worker", export)
        self.assertIn("frontend", export["web"])
        self.assertIn("backend", export["web"])
        self.assertIn("job-runner", export["worker"])


class TestLogSystemNoCoreExtended(unittest.TestCase):
    """
    Test the logging system without a core.
    This test verifies that the logging system can function
    independently without a central logging core.

    Args:
        unittest.TestCase: Inherits from the unittest TestCase class.

    """

    def setUp(self):
        self.groups = []
        self.streams = {}

        for i in range(2):
            group = LogGroup(name=f"app-{i}")
            self.groups.append(group)
            for j in range(2):
                stream = LogStream(name=f"mod-{i}-{j}")
                group.register_stream(stream)
                self.streams[f"{group.name}:{stream.name}"] = stream

    def test_stream_to_group_logging(self):
        for name, stream in self.streams.items():
            for k in range(3):
                stream.info(f"INFO {k}")
                stream.warn(f"WARN {k}")
                stream.error(f"ERROR {k}")
                stream.debug(f"DEBUG {k}")

        time.sleep(0.2)

        for group in self.groups:
            export = group.export()
            self.assertEqual(len(export), 2)
            for logs in export.values():
                self.assertEqual(len(logs), 12)
                self.assertEqual(logs[0]["level"], "INFO")
                self.assertEqual(logs[1]["level"], "WARNING")
                self.assertEqual(logs[2]["level"], "ERROR")
                self.assertEqual(logs[3]["level"], "DEBUG")

    def test_repr_and_dict_consistency(self):
        for group in self.groups:
            self.assertIn("name", group.dict)
            self.assertTrue(str(group).startswith("LogGroup("))
        for stream in self.streams.values():
            self.assertIn("log_format", stream.dict)
            self.assertTrue(str(stream).startswith("LogStream("))

    def test_log_event_identity_consistency(self):
        stream = LogStream(name="test-id")
        group = LogGroup(name="event-test")
        group.register_stream(stream)
        for i in range(2):
            stream.info(f"Event {i}")
        time.sleep(0.1)
        export = group.export()
        for logs in export.values():
            for event in logs:
                self.assertIn("id", event)
                self.assertIn("datestamp", event)
                self.assertTrue(":" in event["name"])


if __name__ == "__main__":
    unittest.main()
