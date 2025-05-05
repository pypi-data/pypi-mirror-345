import unittest
from enum import Enum
from pangu.particle.base.platform_status import BasePlatformStatus


class TestPlatformStatus(unittest.TestCase):

    def test_enum_values_and_descriptions(self):
        self.assertEqual(BasePlatformStatus.READY.value, 3)
        self.assertEqual(BasePlatformStatus.READY.description, "Platform ready")
        self.assertEqual(
            BasePlatformStatus.INIT.dict,
            {"name": "INIT", "value": 1, "description": "Platform nitialized"},
        )

    def test_from_value(self):
        self.assertEqual(BasePlatformStatus.from_value(2), BasePlatformStatus.LOADED)
        self.assertEqual(BasePlatformStatus.from_value(5), BasePlatformStatus.CLOSED)
        with self.assertRaises(ValueError):
            BasePlatformStatus.from_value(99)

    def test_choices(self):
        choices = BasePlatformStatus.choices()
        self.assertIn(("READY", "Platform ready"), choices)
        self.assertEqual(len(choices), 5)

    def test_repr_and_str(self):
        status = BasePlatformStatus.FAILED
        rep = repr(status)
        self.assertIn("FAILED", rep)
        self.assertIn("description=Platform failed", rep)
