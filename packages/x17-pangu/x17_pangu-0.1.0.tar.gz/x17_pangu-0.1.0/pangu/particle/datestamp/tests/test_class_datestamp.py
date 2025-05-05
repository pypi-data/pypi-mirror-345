import unittest
from datetime import datetime

import pytz

from pangu.particle import Datestamp
from pangu.particle.duration.duration import Duration


class TestDatestamp(unittest.TestCase):

    def test_init_basic(self):
        ds = Datestamp(2025, 3, 23, 15, 30)
        self.assertEqual(ds.year, 2025)
        self.assertEqual(ds.month, 3)
        self.assertEqual(ds.day, 23)
        self.assertEqual(ds.hour, 15)
        self.assertEqual(ds.minute, 30)

    def test_init_missing_date(self):
        with self.assertRaises(ValueError):
            Datestamp(hour=12)

    def test_configure_and_get_format(self):
        Datestamp.configure(
            date_format="%d/%m/%Y",
            time_format="%H-%M-%S",
            date_time_format="%d/%m/%Y %H-%M-%S",
            time_zone_name="Asia/Tokyo",
        )
        self.assertEqual(Datestamp.get_date_format(), "%d/%m/%Y")
        self.assertEqual(Datestamp.get_time_format(), "%H-%M-%S")
        self.assertEqual(Datestamp.get_date_time_format(), "%d/%m/%Y %H-%M-%S")
        self.assertEqual(Datestamp.get_time_zone_name(), "Asia/Tokyo")

    def test_now(self):
        ds = Datestamp.now()
        self.assertIsInstance(ds, Datestamp)

    def test_from_datetime(self):
        dt = datetime(2022, 12, 31, 23, 59)
        ds = Datestamp.from_datetime(dt, "UTC")
        self.assertEqual(ds.year, 2022)
        self.assertEqual(ds.hour, 23)

    def test_from_timestamp(self):
        tz = pytz.timezone("UTC")
        dt = tz.localize(datetime(2024, 1, 1, 12, 0))
        timestamp = dt.timestamp()
        ds = Datestamp.from_timestamp(timestamp, "UTC")
        self.assertEqual(ds.year, 2024)
        self.assertEqual(ds.hour, 12)

    def test_from_string(self):
        ds = Datestamp.from_string(
            "2025-03-23 18:30:00", date_time_format="%Y-%m-%d %H:%M:%S"
        )
        self.assertEqual(ds.year, 2025)
        self.assertEqual(ds.hour, 18)

    def test_from_dict(self):
        d = {
            "year": 2025,
            "month": 3,
            "day": 23,
            "hour": 10,
            "minute": 5,
            "second": 45,
            "time_zone_name": "UTC",
        }
        ds = Datestamp.from_dict(d)
        self.assertEqual(ds.year, 2025)
        self.assertEqual(ds.minute, 5)

    def test_str_output(self):
        ds = Datestamp(2025, 3, 23, 10, 0, 0)
        self.assertTrue(isinstance(str(ds), str))
        self.assertIn("2025", str(ds))

    def test_timezone_awareness(self):
        ds = Datestamp(2025, 3, 23, 10, 0, 0, time_zone_name="Asia/Shanghai")
        self.assertEqual(ds.time_zone.zone, "Asia/Shanghai")
        self.assertEqual(ds.time_zone_name, "Asia/Shanghai")

    def test_dst_transition(self):
        # 2024年3月31日是欧洲夏令时的转换点
        ds = Datestamp(2024, 3, 31, 2, 0, 0, time_zone_name="Europe/Paris")
        self.assertEqual(ds.time_zone.zone, "Europe/Paris")
        self.assertEqual(ds.hour, 2)

    def test_repr_formatting(self):
        ds = Datestamp(2025, 3, 23, 14, 55, 30)
        self.assertIn("2025", str(ds))
        self.assertIn("14", str(ds))

    def test_invalid_timezone(self):
        with self.assertRaises(Exception):
            Datestamp(2025, 3, 23, time_zone_name="Invalid/Zone")

    def test_cross_timezone_timestamp(self):
        ds1 = Datestamp(2025, 3, 23, 10, 0, 0, time_zone_name="UTC")
        ds2 = Datestamp(2025, 3, 23, 10, 0, 0, time_zone_name="Asia/Tokyo")
        self.assertNotEqual(ds1.datetime.timestamp(), ds2.datetime.timestamp)

    def test_configure_timezone_only(self):
        Datestamp.configure(time_zone_name="America/New_York")
        self.assertEqual(Datestamp.get_time_zone_name(), "America/New_York")

    def test_init_all_zero(self):
        ds = Datestamp(2025, 1, 1)
        self.assertEqual(ds.hour, 0)
        self.assertEqual(ds.minute, 0)
        self.assertEqual(ds.second, 0)
        self.assertEqual(ds.microsecond, 0)

    def test_configure_partial_format(self):
        Datestamp.configure(date_format="%Y/%m/%d")
        self.assertEqual(Datestamp.get_date_format(), "%Y/%m/%d")

        Datestamp.configure(time_format="%H:%M")
        self.assertEqual(Datestamp.get_time_format(), "%H:%M")

        Datestamp.configure(date_time_format="%Y/%m/%d %H:%M")
        self.assertEqual(Datestamp.get_date_time_format(), "%Y/%m/%d %H:%M")

        Datestamp.reset()

    def test_from_string_with_format_and_timezone(self):
        ds = Datestamp.from_string(
            "23/03/2025 22-45-00",
            date_time_format="%d/%m/%Y %H-%M-%S",
            time_zone_name="Asia/Tokyo",
        )
        self.assertEqual(ds.year, 2025)
        self.assertEqual(ds.hour, 22)
        self.assertEqual(ds.time_zone_name, "Asia/Tokyo")

    def test_set_method_on_instance(self):
        ds = Datestamp(2025, 3, 23)
        ds.set(hour=5, minute=10)
        self.assertEqual(ds.hour, 5)
        self.assertEqual(ds.minute, 10)

        with self.assertRaises(AttributeError):
            ds.set(not_exist=123)

    def test_getters(self):
        ds = Datestamp(2025, 3, 23, 14, 30, 45)
        self.assertIsInstance(ds.get_datetime(), datetime)
        self.assertIsInstance(ds.get_timestamp(), float)

    def test_properties(self):
        ds = Datestamp(2025, 3, 23, 14, 30, 45, time_zone_name="UTC")
        self.assertIsInstance(ds.date_str, str)
        self.assertIsInstance(ds.time_str, str)
        self.assertIsInstance(ds.datestamp_str, str)
        self.assertEqual(ds.dict["year"], 2025)

    def test_operator_add_duration(self):
        ds = Datestamp(2025, 3, 23, 10, 0, 0, time_zone_name="UTC")
        duration = Duration(second=3600)
        new_ds = ds + duration
        self.assertEqual(new_ds.hour, 11)

    def test_operator_radd_duration(self):
        ds = Datestamp(2025, 3, 23, 10, 0, 0, time_zone_name="UTC")
        duration = Duration(second=1800)
        new_ds = duration + ds
        self.assertEqual(new_ds.minute, 30)

    def test_operator_sub_duration(self):
        ds = Datestamp(2025, 3, 23, 10, 0, 0, time_zone_name="UTC")
        duration = Duration(second=600)
        new_ds = ds - duration
        self.assertEqual(new_ds.minute, 50)

    def test_operator_sub_datestamp(self):
        ds1 = Datestamp(2025, 3, 23, 11, 0, 0, time_zone_name="UTC")
        ds2 = Datestamp(2025, 3, 23, 10, 0, 0, time_zone_name="UTC")
        duration = ds1 - ds2
        self.assertEqual(duration.base, 3600)

    def test_operator_comparisons(self):
        ds1 = Datestamp(2025, 3, 23, 11, 0, 0)
        ds2 = Datestamp(2025, 3, 23, 10, 0, 0)
        self.assertTrue(ds1 > ds2)
        self.assertTrue(ds2 < ds1)
        self.assertTrue(ds1 >= ds2)
        self.assertTrue(ds2 <= ds1)
        self.assertTrue(ds1 != ds2)
        self.assertFalse(ds1 == ds2)

    def test_operator_bool_and_hash(self):
        ds = Datestamp(2025, 1, 1)
        self.assertTrue(bool(ds))
        self.assertIsInstance(hash(ds), int)

    def test_describe_and_export(self):
        ds = Datestamp(2025, 3, 23, 12, 34, 56)
        desc = ds.describe()
        text = ds.describe(as_text=True)
        self.assertIn("year", desc)
        self.assertIn("12 hour", text)

    def test_export(self):
        ds = Datestamp(2025, 3, 23, 12, 34, 56)
        exported = ds.export()
        self.assertIn("datestamp", exported)
        self.assertIn("timezone", exported)


if __name__ == "__main__":
    unittest.main()
