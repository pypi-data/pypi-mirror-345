import unittest
from datetime import datetime

import pytz

from pangu.particle.datestamp import Datestamp
from pangu.particle.datestamp.time import Time
from pangu.particle.duration import Duration


class TestTime(unittest.TestCase):

    def test_init_and_repr(self):
        t = Time(14, 30)
        self.assertEqual(t.hour, 14)
        self.assertEqual(t.minute, 30)
        self.assertIn("Time(hour=14", repr(t))

    def test_now(self):
        now = Time.now()
        self.assertIsInstance(now, Time)

    def test_add_duration(self):
        t = Time(14, 0)
        result = t + Duration(minute=30)
        self.assertIsInstance(result, Time)
        self.assertEqual(result.minute, 30)

    def test_sub_duration(self):
        t = Time(14, 30)
        result = t - Duration(minute=15)
        self.assertEqual(result.minute, 15)

    def test_sub_time(self):
        t1 = Time(15, 0)
        t2 = Time(14, 0)
        diff = t1 - t2
        self.assertEqual(diff.hour, 1)

    def test_invalid_add(self):
        t = Time(14)
        with self.assertRaises(TypeError):
            _ = t + 123

    def test_from_string_default_format(self):
        t = Time.from_string("14:45:30")
        self.assertEqual(t.hour, 14)
        self.assertEqual(t.minute, 45)
        self.assertEqual(t.second, 30)

    def test_from_string_custom_format(self):
        t = Time.from_string("02|15", "%H|%M")
        self.assertEqual(t.hour, 2)
        self.assertEqual(t.minute, 15)

    def test_from_timestamp(self):
        ts = datetime(2025, 3, 28, 22, 30, tzinfo=pytz.UTC).timestamp()
        t = Time.from_timestamp(ts, time_zone_name="UTC")
        self.assertEqual(t.hour, 22)
        self.assertEqual(t.minute, 30)

    def test_to_datestamp_all_fields(self):
        t = Time(15, 45, 10, 250000)
        d = t.to_datestamp(year=2025, month=4, day=5, time_zone_name="UTC")
        self.assertIsInstance(d, Datestamp)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 5)
        self.assertEqual(d.hour, 15)
        self.assertEqual(d.minute, 45)
        self.assertEqual(d.microsecond, 250000)
        self.assertEqual(d.time_zone.zone, "UTC")

    def test_to_datestamp_partial_fields(self):
        t = Time(8, 15, 0)
        d = t.to_datestamp(day=20)
        self.assertEqual(d.hour, 8)
        self.assertEqual(d.day, 20)

    def test_to_datestamp_default_inheritance(self):
        t = Time(6, 0, 0)
        d = t.to_datestamp()
        self.assertEqual(d.hour, 6)
        self.assertEqual(d.day, t.day)  # inherited from original datetime

    def test_export(self):
        t = Time(14, 30)
        exported = t.export()
        self.assertEqual(exported["hour"], 14)
        self.assertEqual(exported["minute"], 30)
        self.assertEqual(exported["second"], 0)
        self.assertEqual(exported["microsecond"], 0)
        self.assertIn("time_zone_name", exported)
