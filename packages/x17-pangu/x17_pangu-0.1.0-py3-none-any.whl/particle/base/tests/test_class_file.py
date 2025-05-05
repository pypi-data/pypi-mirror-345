import unittest
from pangu.particle.base.file import BaseFile
from pangu.particle.base.path import BasePath


class DummyPath(BasePath):
    def is_absolute(self):
        return True

    def is_remote(self):
        return False

    def to_uri(self):
        return self.raw


class DummyFile(BaseFile):
    def __init__(self, path, content=None):
        super().__init__(path, content)

    def read(self):
        return self.content or ""

    def write(self, content):
        self.content = content

    def exists(self):
        return self.content is not None


class TestBaseFile(unittest.TestCase):

    def test_init_and_repr(self):
        path = DummyPath("dummy.txt")
        f = DummyFile(path, "hello")
        self.assertEqual(f.read(), "hello")
        self.assertIn("DummyFile", repr(f))

    def test_write_and_read(self):
        path = DummyPath("file.txt")
        f = DummyFile(path)
        f.write("data")
        self.assertEqual(f.read(), "data")

    def test_exists(self):
        self.assertTrue(DummyFile(DummyPath("f.txt"), "data").exists())
        self.assertFalse(DummyFile(DummyPath("empty")).exists())

    def test_to_dict(self):
        f = DummyFile(DummyPath("path.txt"), "hello")
        d = f.to_dict()
        self.assertEqual(d["path"], "path.txt")
        self.assertEqual(d["content"], "hello")

    def test_export(self):
        f = DummyFile(DummyPath("path.txt"), "hello")
        d = f.export()
        self.assertEqual(d["path"], "path.txt")
        self.assertEqual(d["content"], "hello")


if __name__ == "__main__":
    unittest.main()
