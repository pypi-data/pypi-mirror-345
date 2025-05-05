import unittest
from unittest.mock import patch, MagicMock
from pangu.particle.remote.call import Call
from pangu.particle.remote.url import Url
from pangu.particle.remote.response import Response
from pangu.particle.duration import Duration


class TestCall(unittest.TestCase):

    def test_init_and_properties(self):
        call = Call(
            method="POST",
            url="https://example.com/api",
            headers={"Authorization": "Bearer token"},
            query={"page": 1},
            body={"key": "value"},
            timeout=5,
            retry=2,
            interval=Duration(second=1)
        )
        self.assertEqual(call.method, "POST")
        self.assertEqual(call.url.host, "example.com")
        self.assertEqual(call.query["page"], 1)
        self.assertEqual(call.headers["Authorization"], "Bearer token")
        self.assertEqual(call.body["key"], "value")
        self.assertEqual(call.timeout, 5)
        self.assertEqual(call.retry, 2)
        self.assertIsInstance(call.interval, Duration)

    def test_data_property(self):
        call = Call(method="POST", url="https://x.com", body={"a": 1})
        self.assertEqual(call.data, b'{"a": 1}')
        self.assertEqual(call.headers["Content-Type"], "application/json")

        call2 = Call(method="POST", url="https://x.com", body="hello")
        self.assertEqual(call2.data, b"hello")

        call3 = Call(method="POST", url="https://x.com", body=b"bytes")
        self.assertEqual(call3.data, b"bytes")

        with self.assertRaises(ValueError):
            Call(method="POST", url="https://x.com", body=object()).data

    @patch("urllib.request.urlopen")
    def test_send_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.getheaders.return_value = [("Content-Type", "application/json")]
        mock_response.read.return_value = b'{"ok": true}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        call = Call(method="GET", url="https://success.com")
        response = call.send()

        self.assertIsInstance(response, Response)
        self.assertTrue(response.success)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, b'{"ok": true}')
        self.assertEqual(len(call.log), 1)
        self.assertEqual(call.log[0].status, 200)

    @patch("urllib.request.urlopen", side_effect=Exception("Boom"))
    def test_send_retry_on_exception(self, mock_urlopen):
        call = Call(method="GET", url="https://fail.com", retry=2, interval=Duration(millisecond=10))
        response = call.send()

        self.assertFalse(response.success)
        self.assertEqual(call.index, 2)
        self.assertEqual(len(call.log), 2)
        self.assertIn("Boom", call.log[0].message)

    def test_from_dict_and_repr(self):
        data = {
            "method": "PUT",
            "url": "https://api.test/submit",
            "headers": {"X-Test": "1"},
            "query": {"debug": "true"},
            "body": {"test": "yes"},
            "timeout": 3,
            "retry": 1,
            "interval": Duration(second=2)
        }
        call = Call.from_dict(data)
        self.assertEqual(call.method, "PUT")
        self.assertIn("X-Test", call.headers)
        self.assertIn("debug", call.query)
        self.assertIn("test", call.body)
        self.assertIn("Call(", repr(call))
        
    def test_real_http_call(self):
        call = Call(
            method="GET",
            url="https://httpbin.org/get",
            query={"foo": "bar"},
            timeout=5
        )
        response = call.send()
        
        # 检查基本属性
        self.assertIsInstance(response, Response)
        self.assertTrue(response.success)
        self.assertEqual(response.status, 200)
        self.assertIn("application/json", response.headers.get("Content-Type", ""))
        
        # 检查返回内容是否包含参数
        data = response.json()
        self.assertEqual(data["args"]["foo"], "bar")
    
    def test_real_http_get_call(self):
        call = Call(
            method="GET",
            url="https://httpbin.org/get",
            query={"hello": "world"},
            timeout=5,
        )
        response = call.send()
        self.assertIsInstance(response, Response)
        self.assertTrue(response.success)
        self.assertEqual(response.status, 200)

        data = response.json()
        self.assertEqual(data["args"]["hello"], "world")

    def test_real_http_post_call(self):
        call = Call(
            method="POST",
            url="https://httpbin.org/post",
            body={"foo": "bar"},
            timeout=5,
        )
        response = call.send()
        self.assertIsInstance(response, Response)
        self.assertTrue(response.success)
        self.assertEqual(response.status, 200)

        data = response.json()
        self.assertEqual(data["json"]["foo"], "bar")
        self.assertEqual(data["headers"]["Content-Type"], "application/json")
    
    def test_get_with_custom_headers(self):
        call = Call(
            method="GET",
            url="https://httpbin.org/headers",
            headers={"X-Custom-Header": "PanguTest"},
            timeout=5,
        )
        response = call.send()
        self.assertTrue(response.success)
        data = response.json()
        self.assertEqual(data["headers"]["X-Custom-Header"], "PanguTest")

    def test_post_with_custom_headers(self):
        call = Call(
            method="POST",
            url="https://httpbin.org/post",
            headers={"X-Test": "RemoteCall"},
            body={"a": 1},
            timeout=5,
        )
        response = call.send()
        self.assertTrue(response.success)
        data = response.json()
        self.assertEqual(data["headers"]["X-Test"], "RemoteCall")
        self.assertEqual(data["json"]["a"], 1)

    def test_timeout_retry_logging(self):
        call = Call(
            method="GET",
            url="https://httpbin.org/delay/3",
            timeout=1,
            retry=2,
            interval=Duration(second=0.5),
        )
        response = call.send()
        self.assertFalse(response.success)
        self.assertEqual(response.status, 0)
        self.assertGreaterEqual(len(call.log), 2)
        for log in call.log:
            self.assertEqual(log.level, "ERROR")
            self.assertEqual(log.status, 0)


if __name__ == "__main__":
    unittest.main()