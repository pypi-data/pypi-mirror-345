import unittest
from pangu.particle.base.path import BasePath


class DummyPath(BasePath):
    def is_absolute(self) -> bool:
        return self.raw.startswith("/")

    def is_remote(self) -> bool:
        return self.raw.startswith("s3://") or self.raw.startswith("http")

    def to_uri(self) -> str:
        return f"uri://{self.raw}"


class TestBasePath(unittest.TestCase):

    def test_str_repr(self):
        path = DummyPath("/some/path")
        self.assertEqual(str(path), "/some/path")
        self.assertIn("DummyPath", repr(path))

    def test_is_absolute(self):
        self.assertTrue(DummyPath("/abs/path").is_absolute())
        self.assertFalse(DummyPath("rel/path").is_absolute())

    def test_is_remote(self):
        self.assertTrue(DummyPath("s3://bucket/key").is_remote())
        self.assertFalse(DummyPath("/local/file").is_remote())

    def test_to_uri(self):
        path = DummyPath("abc/xyz")
        self.assertEqual(path.to_uri(), "uri://abc/xyz")

    def test_export(self):
        path = DummyPath("/some/path")
        exported = path.export()
        self.assertEqual(exported["raw"], "/some/path")
        self.assertEqual(exported["raw"], path.raw)


if __name__ == "__main__":
    unittest.main()
