import unittest
from pangu.particle.storage.storage import Storage


class TestStorage(unittest.TestCase):

    def test_init_and_dict(self):
        s = Storage(100, "kb")
        self.assertEqual(s.size, 100)
        self.assertEqual(s.unit, "kb")
        self.assertEqual(s.dict["unit"], "kb")

    def test_get_base(self):
        s = Storage(1, "kb")
        self.assertEqual(s.get_base(), 1024.0)

    def test_repr_and_str(self):
        s = Storage(5, "mb")
        self.assertIn("5", repr(s))
        self.assertIn("mb", str(s))

    def test_add_Storage(self):
        s1 = Storage(1, "kb")
        s2 = Storage(1, "kb")
        result = s1 + s2
        self.assertEqual(result.unit, "kb")
        self.assertAlmostEqual(result.size, 2)

    def test_add_number(self):
        s = Storage(10, "mb")
        result = s + 5
        self.assertEqual(result.size, 15)
        self.assertEqual(result.unit, "mb")

    def test_sub_Storage(self):
        s1 = Storage(2, "gb")
        s2 = Storage(1, "gb")
        result = s1 - s2
        self.assertEqual(result.unit, "gb")
        self.assertEqual(result.size, 1)

    def test_sub_number(self):
        s = Storage(10, "mb")
        result = s - 3
        self.assertEqual(result.size, 7)
        self.assertEqual(result.unit, "mb")

    def test_mul(self):
        s = Storage(2, "mb")
        result = s * 3
        self.assertEqual(result.size, 6)
        self.assertEqual(result.unit, "mb")

    def test_eq_Storage(self):
        s1 = Storage(1, "gb")
        s2 = Storage(1024, "mb")
        self.assertTrue(s1 == s2)

    def test_eq_number(self):
        s = Storage(10, "mb")
        self.assertTrue(s == 10)

    def test_to_unit(self):
        s = Storage(1, "gb")
        converted = s.to_unit("mb")
        self.assertAlmostEqual(converted.size, 1024)
        self.assertEqual(converted.unit, "mb")

    def test_as_unit_chainable(self):
        s = Storage(2048, "kb")
        s.as_unit("mb")
        self.assertAlmostEqual(s.size, 2)
        self.assertEqual(s.unit, "mb")

    def test_get_readable_unit(self):
        s = Storage(2048, "kb")
        unit = s.get_readable_unit()
        self.assertEqual(unit, "mb")

    def test_to_readable_conversion(self):
        s = Storage(1536, "kb")
        r = s.to_readable()
        self.assertTrue(isinstance(r, Storage))
        self.assertEqual(r.unit, "mb")
        self.assertAlmostEqual(r.size, 1.5)

    def test_as_readable_chainable(self):
        s = Storage(2048, "kb")
        s.as_readable()
        self.assertEqual(s.unit, "mb")
        self.assertAlmostEqual(s.size, 2)

    def test_export(self):
        s = Storage(100, "kb")
        exported = s.export()
        self.assertEqual(exported["size"], 100)
        self.assertEqual(exported["unit"], "kb")


if __name__ == "__main__":
    unittest.main()
