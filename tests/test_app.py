import os
import tempfile
import unittest

_test_db = tempfile.NamedTemporaryFile(prefix="mdm-test-", suffix=".db", delete=False)
_test_db.close()
os.environ["MDM_DATABASE_PATH"] = _test_db.name
os.environ["MDM_ADMIN_TOKEN"] = "test-token"
os.environ["FLASK_SECRET_KEY"] = "test-secret-key"

from app import create_app  # noqa: E402


class MDMApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)
        cls.client = cls.app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_registration_requires_valid_json_and_udid(self):
        self.assertEqual(self.client.post("/api/devices", data="no-json").status_code, 400)
        response = self.client.post("/api/devices", json={"serial": "abc"})
        self.assertEqual(response.status_code, 400)

    def test_register_device_and_queue_command_requires_admin(self):
        response = self.client.post("/api/devices", json={"udid": "test-device-1", "serial": "SERIAL-1"})
        self.assertEqual(response.status_code, 201)

        denied = self.client.post(
            "/api/devices/test-device-1/commands",
            json={"command_type": "DeviceInformation"},
        )
        self.assertEqual(denied.status_code, 401)

        login = self.client.post("/api/admin/login", json={"token": "test-token"})
        self.assertEqual(login.status_code, 200)
        queued = self.client.post(
            "/api/devices/test-device-1/commands",
            json={"command_type": "DeviceInformation", "payload": {}},
        )
        self.assertEqual(queued.status_code, 202)

    def test_unknown_device_and_invalid_command(self):
        login = self.client.post("/api/admin/login", json={"token": "test-token"})
        self.assertEqual(login.status_code, 200)
        missing = self.client.post(
            "/api/devices/missing/commands",
            json={"command_type": "DeviceInformation"},
        )
        self.assertEqual(missing.status_code, 404)
        invalid = self.client.post(
            "/api/devices/missing/commands",
            json={"command_type": "ArbitraryCommand"},
        )
        self.assertEqual(invalid.status_code, 400)


if __name__ == "__main__":
    unittest.main()
