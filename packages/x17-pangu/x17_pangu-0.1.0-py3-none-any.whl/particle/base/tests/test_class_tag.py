import unittest
from pangu.particle.base.tag import BaseTag


class TestBaseTag(unittest.TestCase):

    def test_init_and_dict(self):
        tag = BaseTag("type", "fruit")
        self.assertEqual(tag.key, "type")
        self.assertEqual(tag.value, "fruit")
        self.assertEqual(tag.dict, {"key": "type", "value": "fruit"})

    def test_from_dict(self):
        tag = BaseTag.from_dict({"key": "color", "value": "blue"})
        self.assertEqual(tag.key, "color")
        self.assertEqual(tag.value, "blue")

        empty_tag = BaseTag.from_dict({})
        self.assertEqual(empty_tag.key, "")
        self.assertEqual(empty_tag.value, "")

    def test_repr_and_str(self):
        tag = BaseTag("color", "red")
        expected = "BaseTag(key=color, value=red)"
        self.assertEqual(str(tag), expected)
        self.assertEqual(repr(tag), expected)

    def test_eq_and_ne(self):
        tag1 = BaseTag("a", 1)
        tag2 = BaseTag("a", 1)
        tag3 = BaseTag("a", 2)
        tag_dict = {"key": "a", "value": 1}

        self.assertTrue(tag1 == tag2)
        self.assertFalse(tag1 != tag2)
        self.assertTrue(tag1 == tag_dict)
        self.assertFalse(tag1 == tag3)
        self.assertTrue(tag1 != tag3)
        self.assertFalse(tag1 == {"key": "b", "value": 1})
        self.assertFalse(tag1 == 123)

    def test_update_options(self):
        tag = BaseTag("x", "y")
        tag.update()
        self.assertEqual(tag.key, "x")
        self.assertEqual(tag.value, "y")

        tag.update(key="z")
        self.assertEqual(tag.key, "z")

        tag.update(value="w")
        self.assertEqual(tag.value, "w")

        tag.update(key="final", value=123)
        self.assertEqual(tag.key, "final")
        self.assertEqual(tag.value, 123)

    def test_export(self):
        tag = BaseTag("test", 999)
        exported = tag.export()
        self.assertEqual(exported, {"key": "test", "value": 999})
