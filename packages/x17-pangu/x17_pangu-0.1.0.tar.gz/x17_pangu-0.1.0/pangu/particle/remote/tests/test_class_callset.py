import unittest
from pangu.particle.remote.call import Call
from pangu.particle.remote.callset import CallSet
from pangu.particle.duration import Duration

class TestCallSet(unittest.TestCase):

    def setUp(self):
        self.call1 = Call(
            method="GET",
            url="https://httpbin.org/get",
            query={"test": "1"},
            timeout=5
        )
        self.call2 = Call(
            method="GET",
            url="https://httpbin.org/get",
            query={"test": "2"},
            timeout=5
        )
        self.callset = CallSet([self.call1, self.call2])

    def test_add_single_call(self):
        call = Call(method="GET", url="https://httpbin.org/status/204")
        self.callset.add(call)
        self.assertEqual(len(self.callset.calls), 3)

    def test_batch_calls(self):
        data = [
            {"method": "GET", "url": "https://httpbin.org/status/200"},
            {"method": "POST", "url": "https://httpbin.org/post", "body": {"x": 1}},
        ]
        self.callset.batch(data)
        self.assertEqual(len(self.callset.calls), 4)

    def test_run(self):
        results = self.callset.run()
        self.assertEqual(len(results), 2)
        for res in results:
            self.assertTrue(res.status >= 200 and res.status < 300)

    def test_repr_str(self):
        r1 = repr(self.callset)
        r2 = str(self.callset)
        self.assertIn("CallSet", r1)
        self.assertIn("CallSet", r2)

    def test_dict_export(self):
        self.callset.run()
        data = self.callset.dict
        self.assertIn("calls", data)
        self.assertIn("results", data)
        self.assertIn("logs", data)
        self.assertEqual(len(data["calls"]), 2)
        self.assertEqual(len(data["results"]), 2)

    def test_result_export(self):
        self.callset.run()
        self.assertEqual(len(self.callset.results), 2)

    def test_log_integrity(self):
        self.callset.run()
        logs = self.callset.logs
        self.assertEqual(len(logs), 2)
        for log in logs:
            self.assertIn("message", log.dict)
            self.assertIn("status", log.dict)

if __name__ == "__main__":
    unittest.main()