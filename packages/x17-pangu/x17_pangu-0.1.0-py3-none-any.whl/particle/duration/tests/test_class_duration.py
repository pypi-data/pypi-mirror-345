import unittest
from datetime import timedelta

from dateutil.relativedelta import relativedelta  # type: ignore

from pangu.particle.duration.duration import Duration


class TestDuration(unittest.TestCase):

    def test_init(self):
        d = Duration(year=1, day=2, second=30)
        self.assertEqual(d.year, 1)
        self.assertEqual(d.day, 2)
        self.assertEqual(d.second, 30)

    def test_dict(self):
        d = Duration(minute=3)
        self.assertIn("minute", d.dict)
        self.assertEqual(d.dict["minute"], 3)

    def test_base(self):
        d = Duration(hour=1)
        self.assertEqual(d.base, 3600)

    def test_normalize(self):
        d = Duration(second=90)
        d.as_normalize()
        self.assertEqual(d.minute, 1)
        self.assertEqual(d.second, 30)

    def test_add(self):
        d1 = Duration(day=1, hour=2)
        d2 = Duration(hour=1)
        d3 = d1 + d2
        self.assertEqual(d3.hour, 3)
        self.assertEqual(d3.day, 1)

    def test_sub(self):
        d1 = Duration(day=1, hour=3)
        d2 = Duration(hour=1)
        d3 = d1 - d2
        self.assertEqual(d3.hour, 2)

    def test_eq(self):
        d1 = Duration(minute=5)
        d2 = Duration(minute=5)
        self.assertTrue(d1 == d2)

    def test_ne(self):
        d1 = Duration(minute=5)
        d2 = Duration(minute=3)
        self.assertTrue(d1 != d2)

    def test_comparison(self):
        d1 = Duration(second=30)
        d2 = Duration(second=60)
        self.assertTrue(d1 < d2)
        self.assertTrue(d2 > d1)
        self.assertTrue(d1 <= d2)
        self.assertTrue(d2 >= d1)

    def test_radd(self):
        d1 = Duration(second=10)
        result = sum([d1, d1], Duration())
        self.assertEqual(result.second, 20)

    def test_mul(self):
        d = Duration(minute=2)
        result = d * 3
        self.assertEqual(result.minute, 6)

    def test_truediv(self):
        d = Duration(minute=10)
        result = d / 2
        self.assertEqual(result.minute, 5)

    def test_from_dict(self):
        d = Duration.from_dict({"hour": 2, "minute": 30})
        self.assertEqual(d.hour, 2)
        self.assertEqual(d.minute, 30)

    def test_from_timedelta(self):
        td = timedelta(days=2, seconds=3600)
        d = Duration.from_timedelta(td)
        self.assertEqual(d.day, 2)
        self.assertEqual(d.hour, 1)

    def test_from_relativedelta(self):
        rd = relativedelta(years=1, months=2, days=3)
        d = Duration.from_relativedelta(rd)
        self.assertEqual(d.year, 1)
        self.assertEqual(d.month, 2)
        self.assertEqual(d.day, 3)

    def test_describe_basic(self):
        d = Duration(year=1, month=2, day=3, minute=1)
        desc = d.describe(as_text=True)
        self.assertIn("1 year", desc)
        self.assertIn("2 month", desc)
        self.assertIn("3 day", desc)
        self.assertIn("1 minute", desc)

    def test_describe_zero(self):
        d = Duration()
        self.assertEqual(d.describe(as_text=True), "0 second")

    def test_describe_singular_plural(self):
        d = Duration(year=1, month=1, day=1, second=1)
        self.assertEqual(d.describe(as_text=True), "1 year, 1 month, 1 day, 1 second")

        d2 = Duration(year=2, month=3, second=0)
        self.assertEqual(d2.describe(as_text=True), "2 year, 3 month")

    def test_describe_as_dict(self):
        d = Duration(year=1, month=2, day=3)
        desc = d.describe(as_text=False)
        self.assertEqual(desc["year"], 1)
        self.assertEqual(desc["month"], 2)
        self.assertEqual(desc["day"], 3)

    def test_describe_as_dict_zero(self):
        d = Duration()
        desc = d.describe(as_text=False)
        self.assertEqual(desc["second"], 0)
        self.assertEqual(desc["minute"], 0)
        self.assertEqual(desc["hour"], 0)
        self.assertEqual(desc["day"], 0)
        self.assertEqual(desc["month"], 0)
        self.assertEqual(desc["year"], 0)
        self.assertEqual(desc["microsecond"], 0)
        self.assertEqual(desc["week"], 0)

    def test_export(self):
        d = Duration(year=1, month=2, day=3)
        export_data = d.export()
        self.assertEqual(export_data["year"], 1)
        self.assertEqual(export_data["month"], 2)
        self.assertEqual(export_data["day"], 3)
        self.assertEqual(export_data["hour"], 0)
        self.assertEqual(export_data["minute"], 0)

        d2 = Duration.from_dict(export_data)
        self.assertEqual(d2.year, 1)
        self.assertEqual(d2.month, 2)
        self.assertEqual(d2.day, 3)
        self.assertEqual(d2.hour, 0)
        self.assertEqual(d2.minute, 0)

    def test_set_method_updates_fields(self):
        d = Duration()
        d.set(year=2, second=30, hour=1)
        self.assertEqual(d.year, 2)
        self.assertEqual(d.second, 30)
        self.assertEqual(d.hour, 1)

    def test_set_method_ignores_invalid_keys(self):
        d = Duration()
        d.set(invalid_key=123)  # should not raise error
        self.assertFalse(hasattr(d, "invalid_key"))

    def test_set_precise_mode(self):
        Duration.set_precise()
        d = Duration(year=1)
        # 检查 base 是否大约等于 365.25 天
        approx_seconds = 365.25 * 86400
        self.assertAlmostEqual(
            d.base, approx_seconds, delta=5000
        )  # 放宽容差避免测试误差

    def test_nanosecond_initialization(self):
        d = Duration(nanosecond=999)
        self.assertEqual(d.nanosecond, 999)

    def test_nanosecond_in_dict_and_export(self):
        d = Duration(nanosecond=500)
        self.assertEqual(d.dict["nanosecond"], 500)
        self.assertEqual(d.export()["nanosecond"], 500)

    def test_hash_and_bool(self):
        d1 = Duration(minute=1)
        d2 = Duration()
        self.assertTrue(bool(d1))
        self.assertFalse(bool(d2))
        self.assertIsInstance(hash(d1), int)

    def test_repr_and_str_output(self):
        d = Duration(year=1, day=2)
        text = str(d)
        self.assertIn("year=1", text)
        self.assertIn("day=2", text)

    def test_add_timedelta(self):
        d1 = Duration(second=30)
        td = timedelta(seconds=45)
        result = d1 + td
        self.assertEqual(result.second, 15)
        self.assertEqual(result.minute, 1)
        self.assertEqual(result.hour, 0)

    def test_add_relativedelta(self):
        d1 = Duration(month=1)
        rd = relativedelta(months=2)
        result = d1 + rd
        self.assertEqual(result.month, 3)

    def test_sub_timedelta(self):
        d1 = Duration(minute=3)
        td = timedelta(seconds=60)
        result = d1 - td
        self.assertGreaterEqual(result.second, 0)
        self.assertEqual(result.minute, 2)
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.day, 0)

    def test_sub_relativedelta(self):
        d1 = Duration(month=5)
        rd = relativedelta(months=2)
        result = d1 - rd
        self.assertEqual(result.month, 3)

    def test_mul_float_and_int(self):
        d = Duration(minute=2)
        d2 = d * 1.5
        self.assertEqual(d2.minute, 3)
        d3 = d * 2
        self.assertEqual(d3.minute, 4)

    def test_div_valid_and_invalid(self):
        d = Duration(hour=2)
        d2 = d / 2
        self.assertEqual(d2.hour, 1)
        with self.assertRaises(ValueError):
            d / 0
        with self.assertRaises(ValueError):
            d / "abc"

    def test_export(self):
        d = Duration(year=1, month=2, day=3)
        export_data = d.export()
        self.assertEqual(export_data["year"], 1)
        self.assertEqual(export_data["month"], 2)
        self.assertEqual(export_data["day"], 3)
        self.assertEqual(export_data["hour"], 0)
        self.assertEqual(export_data["minute"], 0)
        self.assertEqual(export_data["second"], 0)
        self.assertEqual(export_data["microsecond"], 0)
        self.assertEqual(export_data["nanosecond"], 0)


if __name__ == "__main__":
    unittest.main()
