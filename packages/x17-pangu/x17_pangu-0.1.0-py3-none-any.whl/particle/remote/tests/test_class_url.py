import unittest
from urllib.parse import urlencode
from pangu.particle.remote.url import Url


class TestUrl(unittest.TestCase):

    def test_init_basic(self):
        url = Url(scheme="http", host="example.com", path="/api", port=8080)
        self.assertEqual(url.scheme, "http")
        self.assertEqual(url.host, "example.com")
        self.assertEqual(url.port, 8080)
        self.assertEqual(url.path, "/api")

    def test_init_from_url_string(self):
        url = Url(url="https://user:pass@example.com:443/api/v1?x=1")
        self.assertEqual(url.scheme, "https")
        self.assertEqual(url.user, "user")
        self.assertEqual(url.password, "pass")
        self.assertEqual(url.host, "example.com")
        self.assertEqual(url.port, 443)
        self.assertEqual(url.path, "/api/v1")
        self.assertEqual(url.query, {"x": ["1"]})

    def test_from_str(self):
        url = Url.from_str("http://a.com:9000/test?y=2")
        self.assertEqual(url.scheme, "http")
        self.assertEqual(url.host, "a.com")
        self.assertEqual(url.port, 9000)
        self.assertEqual(url.path, "/test")
        self.assertEqual(url.query, {"y": ["2"]})

    def test_from_dict(self):
        data = {
            "scheme": "https",
            "host": "api.test",
            "port": 8000,
            "path": "/v1/data",
            "query": {"k": ["v"]},
            "user": "admin",
            "password": "1234",
        }
        url = Url.from_dict(data)
        self.assertEqual(url.scheme, "https")
        self.assertEqual(url.path, "/v1/data")
        self.assertEqual(url.query, {"k": ["v"]})
        self.assertEqual(url.user, "admin")

    def test_link_property(self):
        url = Url(
            scheme="https", host="api.example.com", query={"a": "1", "b": ["2", "3"]}
        )
        link = url.link
        expected_query = urlencode(url.query, doseq=True)
        self.assertTrue(link.startswith("https://api.example.com"))
        self.assertIn(expected_query, link)

    def test_dict_and_attr(self):
        url = Url(host="abc.com", query={"k": ["v"]})
        d = url.dict
        self.assertEqual(d["host"], "abc.com")
        self.assertEqual(d["query"], {"k": ["v"]})
        self.assertIn("link", d)

    def test_path_ops(self):
        url = Url(host="x.com", path="/api")
        new_url = url.join_path("v1", "users")
        self.assertEqual(new_url.path, "/api/v1/users")
        self.assertEqual((url / "v2").path, "/api/v2")
        self.assertEqual((url + "v3").path, "/api/v3")

    def test_join_query(self):
        url = Url(query={"key": ["1"]})
        new_url = url.join_query("key", "2")
        self.assertEqual(new_url.query["key"], ["1", "2"])

    def test_remove_query(self):
        url = Url(query={"remove": ["yes"], "keep": ["ok"]})
        url.remove_query("remove")
        self.assertNotIn("remove", url.query)
        self.assertIn("keep", url.query)

    def test_parent(self):
        url = Url(path="/api/v1/users")
        self.assertEqual(url.parent().path, "/api/v1")
        root_url = Url(path="/")
        self.assertEqual(root_url.parent().path, "/")

    def test_export(self):
        url = Url(host="example.com", path="/test", query={"key": ["value"]})
        exported = url.export()
        self.assertEqual(exported["host"], "example.com")
        self.assertEqual(exported["path"], "/test")
        self.assertEqual(exported["query"], {"key": ["value"]})

    def test_repr(self):
        url = Url(host="example.com", path="/test")
        self.assertEqual(
            repr(url),
            "Url(link='https://example.com/test', scheme='https', host='example.com', path='/test')",
        )


if __name__ == "__main__":
    unittest.main()
