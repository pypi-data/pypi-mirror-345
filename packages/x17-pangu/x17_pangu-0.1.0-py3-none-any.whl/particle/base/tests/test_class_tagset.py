import unittest
from pangu.particle.base.tagset import BaseTagSet
from pangu.particle.base.tag import BaseTag


class TestBaseTagSet(unittest.TestCase):

    def test_init(self):
        tagset = BaseTagSet()
        self.assertEqual(tagset.dict, {})
        tagset = BaseTagSet({"a": 1})
        self.assertEqual(tagset.dict, {"a": 1})

    def test_get_set_delete_item(self):
        tagset = BaseTagSet()
        tagset["x"] = 10
        self.assertEqual(tagset["x"], 10)
        del tagset["x"]
        self.assertIsNone(tagset["x"])

    def test_insert_and_update(self):
        tagset = BaseTagSet()
        tagset.insert("key1", "val1")
        self.assertEqual(tagset["key1"], "val1")
        tagset.update("key1", "updated")
        self.assertEqual(tagset["key1"], "updated")
        tagset.update({"key2": "val2", "key3": 3})
        self.assertEqual(tagset["key2"], "val2")
        self.assertEqual(tagset["key3"], 3)

    def test_find_and_delete(self):
        tagset = BaseTagSet({"a": "b"})
        self.assertEqual(tagset.find("a"), "b")
        tagset.delete("a")
        self.assertIsNone(tagset.find("a"))

    def test_export_and_repr(self):
        tagset = BaseTagSet({"x": "1"})
        self.assertEqual(tagset.export(), {"x": "1"})
        self.assertIn("x=1", repr(tagset))

    def test_equality(self):
        a = BaseTagSet({"a": 1})
        b = BaseTagSet({"a": 1})
        c = {"a": 1}
        d = BaseTagSet({"a": 2})
        self.assertTrue(a == b)
        self.assertTrue(a == c)
        self.assertFalse(a == d)

    def test_list_and_list_tags(self):
        tagset = BaseTagSet({"k1": "v1", "k2": "v2"})
        self.assertIn({"k1": "v1"}, tagset.list())
        tags = tagset.list_tags()
        self.assertEqual(len(tags), 2)
        self.assertTrue(all(isinstance(tag, BaseTag) for tag in tags))

    def test_prefix_and_fuzzy(self):
        tagset = BaseTagSet({"color": "red", "code": "123", "category": "clothing"})
        prefix_matches = tagset.find_by_prefix("co")
        self.assertEqual(len(prefix_matches), 2)
        fuzzy_matches = tagset.find_by_fuzzy("red")
        self.assertEqual(len(fuzzy_matches), 1)
        fuzzy_matches_2 = tagset.find_by_fuzzy("cloth")
        self.assertEqual(len(fuzzy_matches_2), 1)


if __name__ == "__main__":
    unittest.main()
