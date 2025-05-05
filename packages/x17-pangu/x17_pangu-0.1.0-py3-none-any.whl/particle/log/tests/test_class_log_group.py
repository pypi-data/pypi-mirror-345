import unittest
import time
from pangu.particle.log.log_event import LogEvent
from pangu.particle.log.log_group import LogGroup
from pangu.particle.log.log_stream import LogStream
from pangu.particle.log.log_core import LogCore


class TestLogGroup(unittest.TestCase):

    def test_initialization_and_properties(self):
        group = LogGroup(name="platform")
        self.assertIn("platform", group.name)
        self.assertIsNone(group.core)
        self.assertTrue(group.id)
        self.assertIsInstance(group.dict, dict)
        self.assertEqual(group.dict["name"], group.name)
        self.assertEqual(str(group), repr(group))

    def test_register_stream(self):
        group = LogGroup(name="system")
        stream = LogStream(name="auth")
        result = group.register_stream(stream)
        self.assertIs(result.group, group)

    def test_receive_and_export(self):
        group = LogGroup(name="data")
        event = LogEvent(message="testing", level="debug")
        group.receive("stream1", event)
        time.sleep(0.1)
        export = group.export()
        self.assertIn("stream1", export)
        self.assertEqual(export["stream1"][0]["message"], "testing")
        self.assertEqual(export["stream1"][0]["level"], "DEBUG")

    def test_group_with_core_forwarding(self):
        core = LogCore()
        group = LogGroup(name="coretest", core=core)
        event = LogEvent(message="pushed to core", level="info")
        group.receive("streamA", event)
        time.sleep(0.1)
        core_export = core.export(group.name, "streamA")
        self.assertEqual(core_export[0]["message"], "pushed to core")


if __name__ == "__main__":
    unittest.main()
