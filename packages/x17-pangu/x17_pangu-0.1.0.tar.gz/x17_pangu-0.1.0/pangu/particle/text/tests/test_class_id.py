import unittest
from pangu.particle.text.id import Id


class TestClassId(unittest.TestCase):

    def test_class_id_uuid(self):
        id1 = Id.uuid(8)
        id2 = Id.uuid(8)
        self.assertNotEqual(id1, id2, "UUIDs should be unique")
        self.assertEqual(len(id1), 8, "UUID length should be 8")
        self.assertEqual(len(id2), 8, "UUID length should be 8")
        self.assertIsInstance(id1, str, "UUID should be a string")
        self.assertIsInstance(id2, str, "UUID should be a string")

    def test_class_id_random(self):
        id1 = Id.random(8)
        id2 = Id.random(8)
        self.assertNotEqual(id1, id2, "Random IDs should be unique")
        self.assertEqual(len(id1), 8, "Random ID length should be 8")
        self.assertEqual(len(id2), 8, "Random ID length should be 8")
        self.assertIsInstance(id1, str, "Random ID should be a string")
        self.assertIsInstance(id2, str, "Random ID should be a string")

    def test_class_id_random_with_options(self):
        id1 = Id.random(8, include_letters=True, include_numbers=True)
        id2 = Id.random(8, include_letters=True, include_numbers=True)
        self.assertNotEqual(id1, id2, "Random IDs should be unique")
        self.assertEqual(len(id1), 8, "Random ID length should be 8")
        self.assertEqual(len(id2), 8, "Random ID length should be 8")
        self.assertIsInstance(id1, str, "Random ID should be a string")
        self.assertIsInstance(id2, str, "Random ID should be a string")

    def test_class_id_random_with_upper(self):
        id1 = Id.random(8, include_upper=True)
        id2 = Id.random(8, include_upper=True)
        self.assertNotEqual(id1, id2, "Random IDs should be unique")
        self.assertEqual(len(id1), 8, "Random ID length should be 8")
        self.assertEqual(len(id2), 8, "Random ID length should be 8")
        self.assertIsInstance(id1, str, "Random ID should be a string")
        self.assertIsInstance(id2, str, "Random ID should be a string")
        self.assertTrue(
            any(c.isupper() for c in id1), "Random ID should contain uppercase letters"
        )
        self.assertTrue(
            any(c.isupper() for c in id2), "Random ID should contain uppercase letters"
        )

    def test_class_id_random_with_lower(self):
        id1 = Id.random(8, include_lower=True)
        id2 = Id.random(8, include_lower=True)
        self.assertNotEqual(id1, id2, "Random IDs should be unique")
        self.assertEqual(len(id1), 8, "Random ID length should be 8")
        self.assertEqual(len(id2), 8, "Random ID length should be 8")
        self.assertIsInstance(id1, str, "Random ID should be a string")
        self.assertIsInstance(id2, str, "Random ID should be a string")
        self.assertTrue(
            any(c.islower() for c in id1), "Random ID should contain lowercase letters"
        )
        self.assertTrue(
            any(c.islower() for c in id2), "Random ID should contain lowercase letters"
        )

    def test_class_id_random_with_numbers(self):
        id1 = Id.random(8, include_numbers=True)
        id2 = Id.random(8, include_numbers=True)
        self.assertNotEqual(id1, id2, "Random IDs should be unique")
        self.assertEqual(len(id1), 8, "Random ID length should be 8")
        self.assertEqual(len(id2), 8, "Random ID length should be 8")
        self.assertIsInstance(id1, str, "Random ID should be a string")
        self.assertIsInstance(id2, str, "Random ID should be a string")


if __name__ == "__main__":
    unittest.main()
