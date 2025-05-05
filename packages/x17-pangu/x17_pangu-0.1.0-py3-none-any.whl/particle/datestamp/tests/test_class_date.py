import unittest
from datetime import datetime

import pytz

from pangu.particle.datestamp.date import Date
from pangu.particle.datestamp.time import Time
from pangu.particle.duration import Duration


class TestDate(unittest.TestCase):

    def test_init_and_repr(self):
        d = Date(2025, 3, 24)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 3)
        self.assertEqual(d.day, 24)
        self.assertIn("Date(year=2025", repr(d))

    def test_today(self):
        today = Date.today()
        self.assertIsInstance(today, Date)

    def test_add_duration(self):
        d = Date(2025, 3, 24)
        result = d + Duration(day=3)
        self.assertIsInstance(result, Date)
        self.assertEqual(result.day, 27)

    def test_sub_duration(self):
        d = Date(2025, 3, 24)
        result = d - Duration(day=4)
        self.assertEqual(result.day, 20)

    def test_sub_date(self):
        d1 = Date(2025, 3, 30)
        d2 = Date(2025, 3, 25)
        diff = d1 - d2
        self.assertIsInstance(diff, Duration)
        self.assertEqual(diff.day, 5)

    def test_invalid_add(self):
        d = Date(2025, 3, 24)
        with self.assertRaises(TypeError):
            _ = d + 123

    def test_combine_with_time(self):
        d = Date(2025, 3, 24)
        t = Time(14, 30)
        combined = d.combine(t)
        self.assertEqual(combined.year, 2025)
        self.assertEqual(combined.hour, 14)

    def test_from_string_default_format(self):
        d = Date.from_string("2025-03-28")
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 3)
        self.assertEqual(d.day, 28)

    def test_from_string_custom_format(self):
        d = Date.from_string("28/03/2025", "%d/%m/%Y")
        self.assertEqual(d.month, 3)

    def test_from_timestamp(self):
        ts = datetime(2025, 3, 28, 14, 30, tzinfo=pytz.UTC).timestamp()
        d = Date.from_timestamp(ts, time_zone_name="UTC")
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.day, 28)

    def test_time_to_datestamp_full(self):
        t = Time(14, 30)
        dt = t.to_datestamp(year=2025, month=3, day=28)
        self.assertEqual(dt.year, 2025)
        self.assertEqual(dt.hour, 14)

    def test_time_to_datestamp_partial(self):
        t = Time(9, 15)
        dt = t.to_datestamp(day=5)
        self.assertEqual(dt.day, 5)
        self.assertEqual(dt.hour, 9)

    def test_time_to_datestamp_with_timezone(self):
        t = Time(10, 0, time_zone_name="Asia/Tokyo")
        dt = t.to_datestamp(year=2025, month=4, day=1, time_zone_name="UTC")
        self.assertEqual(dt.time_zone.zone, "UTC")

    def test_date_to_datestamp_full(self):
        d = Date(2025, 3, 28)
        dt = d.to_datestamp(hour=14, minute=30, second=15, microsecond=100000)
        self.assertEqual(dt.hour, 14)
        self.assertEqual(dt.microsecond, 100000)

    def test_date_to_datestamp_with_timezone(self):
        d = Date(2025, 3, 28, time_zone_name="Asia/Shanghai")
        dt = d.to_datestamp(time_zone_name="UTC")
        self.assertEqual(dt.time_zone.zone, "UTC")

    def test_export(self):
        d = Date(2025, 3, 28)
        exported = d.export()
        self.assertEqual(exported["year"], 2025)
        self.assertEqual(exported["month"], 3)
        self.assertEqual(exported["day"], 28)
        self.assertIn("time_zone_name", exported)


if __name__ == "__main__":
    unittest.main()
