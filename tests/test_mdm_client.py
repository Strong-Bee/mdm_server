import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).parents[1] / "integrations" / "tr4mpass" / "mdm_client.py"
SPEC = importlib.util.spec_from_file_location("mdm_client", MODULE_PATH)
mdm_client = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mdm_client)


class MdmClientTests(unittest.TestCase):
    def test_remote_http_is_rejected(self):
        with self.assertRaises(ValueError):
            mdm_client.validate_base_url("http://mdm.example.com")

    def test_https_and_local_http_are_allowed(self):
        self.assertEqual(mdm_client.validate_base_url("https://mdm.example.com/"), "https://mdm.example.com")
        self.assertEqual(mdm_client.validate_base_url("http://127.0.0.1:8000/"), "http://127.0.0.1:8000")

    def test_request_uses_bearer_token_and_json(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b'{"status":"queued"}'

        with patch.object(mdm_client, "urlopen", return_value=Response()) as mocked_urlopen:
            result = mdm_client.request_json(
                "https://mdm.example.com", "secret", "/api/devices/UDID/commands",
                method="POST", payload={"command_type": "DeviceInformation", "payload": {}},
            )
        self.assertEqual(result, {"status": "queued"})
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        self.assertEqual(json.loads(request.data), {
            "command_type": "DeviceInformation", "payload": {}
        })


if __name__ == "__main__":
    unittest.main()
