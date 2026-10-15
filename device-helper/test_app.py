import io
import json
import os
import sys
import plistlib
import tempfile
import unittest
import zipfile
from unittest.mock import patch

os.environ["IPHONE_HELPER_TOKEN"] = "test-helper-token"
sys.path.insert(0, os.path.dirname(__file__))
from app import app  # noqa: E402


class HelperApiTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.headers = {"Authorization": "Bearer test-helper-token"}

    def test_health_does_not_require_token(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["service"], "iphone-local-helper")

    def test_devices_requires_token(self):
        self.assertEqual(self.client.get("/api/devices").status_code, 401)

    @patch("app.subprocess.run")
    @patch("app.shutil.which", return_value="/usr/bin/pymobiledevice3")
    def test_device_discovery_parses_cli_json(self, _which, run):
        run.return_value.returncode = 0
        run.return_value.stdout = json.dumps([{"udid": "TEST-UDID", "product_type": "iPhone15,2", "secret": "not returned"}])
        run.return_value.stderr = ""
        response = self.client.get("/api/devices", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["count"], 1)
        self.assertEqual(response.get_json()["devices"][0]["udid"], "TEST-UDID")
        self.assertNotIn("secret", response.get_json()["devices"][0])
        self.assertEqual(run.call_args.kwargs["shell"], False)
        self.assertEqual(run.call_args.kwargs["timeout"], 25)


    @patch("app.subprocess.run")
    @patch("app.shutil.which", return_value="/usr/bin/pymobiledevice3")
    def test_device_info_returns_allowlisted_fields(self, _which, run):
        run.return_value.returncode = 0
        run.return_value.stdout = json.dumps({
            "DeviceName": "Test iPhone",
            "ProductType": "iPhone15,2",
            "ProductVersion": "17.0",
            "WiFiAddress": "00:11:22:33:44:55",
            "PairRecord": {"secret": "hidden"},
        })
        run.return_value.stderr = ""
        response = self.client.get("/api/devices/12345678-ABCD/info", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["info"]["ProductType"], "iPhone15,2")
        self.assertNotIn("WiFiAddress", response.get_json()["info"])
        self.assertNotIn("PairRecord", response.get_json()["info"])
        self.assertEqual(run.call_args.kwargs["env"]["PYMOBILEDEVICE3_UDID"], "12345678-ABCD")
        self.assertFalse(run.call_args.kwargs["shell"])

    def test_device_info_rejects_invalid_udid(self):
        response = self.client.get("/api/devices/../../bad/info", headers=self.headers)
        self.assertIn(response.status_code, (400, 404))

    def test_firmware_rejects_wrong_extension(self):
        response = self.client.post(
            "/api/firmware/inspect",
            headers=self.headers,
            data={"ipsw": (io.BytesIO(b"not ipsw"), "sample.zip")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 415)

    def test_firmware_inspects_manifest_without_extracting(self):
        manifest = {
            "ProductVersion": "17.0",
            "ProductBuildVersion": "21A329",
            "SupportedProductTypes": ["iPhone15,2"],
            "BuildIdentities": [{"Manifest": {"iBSS": {}, "KernelCache": {}}}],
        }
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("BuildManifest.plist", plistlib.dumps(manifest))
            archive.writestr("some/component", b"component-data")
        payload.seek(0)
        response = self.client.post(
            "/api/firmware/inspect",
            headers=self.headers,
            data={"ipsw": (payload, "test.ipsw")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        result = response.get_json()
        self.assertEqual(result["product_version"], "17.0")
        self.assertEqual(result["build_version"], "21A329")
        self.assertIn("KernelCache", result["component_names"])
        self.assertEqual(result["inspection"], "metadata-only; no firmware components extracted or modified")

    def test_firmware_rejects_invalid_zip(self):
        response = self.client.post(
            "/api/firmware/inspect",
            headers=self.headers,
            data={"ipsw": (io.BytesIO(b"broken"), "broken.ipsw")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
