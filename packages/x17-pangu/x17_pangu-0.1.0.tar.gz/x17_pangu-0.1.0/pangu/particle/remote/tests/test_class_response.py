import json
import unittest
from pangu.particle.remote.response import Response
from pangu.particle.remote.url import Url


class TestResponse(unittest.TestCase):

    def test_init_with_url_string(self):
        res = Response(
            status=200,
            headers={"Content-Type": "text/plain"},
            body=b"Hello, world!",
            url="https://example.com",
        )
        self.assertEqual(res.status, 200)
        self.assertIsInstance(res.url, Url)
        self.assertEqual(str(res.url), "https://example.com")

    def test_init_with_url_object(self):
        url = Url("https://example.com/api")
        res = Response(status=201, headers={}, body=b"", url=url)
        self.assertEqual(res.url, url)

    def test_success_property(self):
        self.assertTrue(Response(status=200).success)
        self.assertFalse(Response(status=404).success)

    def test_encoding_and_text(self):
        headers = {"Content-Type": "text/html; charset=iso-8859-1"}
        body = "Café".encode("iso-8859-1")
        res = Response(status=200, headers=headers, body=body)
        self.assertEqual(res.encoding, "iso-8859-1")
        self.assertIn("Café", res.text)

    def test_default_encoding(self):
        res = Response(status=200, headers={}, body=b"hello")
        self.assertEqual(res.encoding, "utf-8")
        self.assertEqual(res.text, "hello")

    def test_dict_and_export(self):
        res = Response(
            status=200,
            headers={"X-Test": "yes"},
            body=b"data",
            url="https://test.url",
            error="Something failed",
        )
        self.assertEqual(res.dict["status"], 200)
        self.assertEqual(res.export()["error"], "Something failed")

    def test_repr_and_str(self):
        res = Response(status=200, body=b"Test", url="https://test.url")
        representation = repr(res)
        self.assertIn("Response(", representation)
        self.assertEqual(str(res), representation)

    def test_from_dict(self):
        data = {
            "status": 500,
            "headers": {"X": "1"},
            "body": b"fail",
            "url": "https://fail.url",
            "error": "Internal error",
        }
        res = Response.from_dict(data)
        self.assertEqual(res.status, 500)
        self.assertEqual(res.url.link, "https://fail.url")

    def test_from_json(self):
        json_str = json.dumps(
            {
                "status": 201,
                "headers": {"Content-Type": "application/json"},
                "body": "",  # JSON string body
                "url": "https://json.url",
                "error": "",
            }
        )
        res = Response.from_json(json_str)
        self.assertEqual(res.status, 201)
        self.assertEqual(str(res.url), "https://json.url")

    def test_json_success_and_failure(self):
        res = Response(status=200, body=json.dumps({"msg": "ok"}).encode("utf-8"))
        self.assertEqual(res.json(), {"msg": "ok"})

        bad_res = Response(status=200, body=b"{invalid: json}")
        with self.assertRaises(json.JSONDecodeError):
            bad_res.json()
        self.assertEqual(bad_res.json(check=False), {})


if __name__ == "__main__":
    unittest.main()
