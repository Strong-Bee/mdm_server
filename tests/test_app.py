import os
import plistlib
import tempfile
import unittest

_test_db = tempfile.NamedTemporaryFile(prefix="mdm-test-", suffix=".db", delete=False)
_test_db.close()
os.environ["MDM_DATABASE_PATH"] = _test_db.name
os.environ["MDM_ADMIN_TOKEN"] = "test-token"
os.environ["FLASK_SECRET_KEY"] = "test-secret-key"

from app import create_app  # noqa: E402


def plist_request(client, path, message, method="put"):
    body = plistlib.dumps(message, fmt=plistlib.FMT_XML)
    return getattr(client, method)(
        path,
        data=body,
        content_type="application/x-apple-aspen-mdm",
    )


class MDMApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)
        cls.client = cls.app.test_client()

    def setUp(self):
        # Initialize the route-managed SQLite schema before clearing test data.
        self.client.get("/health")
        # Keep tests independent even though they share one test database.
        with self.app.app_context():
            from app.routes import _connect
            conn = _connect()
            conn.execute("DELETE FROM commands")
            conn.execute("DELETE FROM devices")
            conn.commit()
            conn.close()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")
        self.assertEqual(response.get_json()["service"], "apple-ios-mdm")

    def test_checkin_rejects_non_plist(self):
        response = self.client.put("/checkin", data="not-a-plist")
        self.assertEqual(response.status_code, 400)

    def test_authenticate_and_token_update_checkin(self):
        authenticate = plist_request(
            self.client,
            "/checkin",
            {
                "MessageType": "Authenticate",
                "UDID": "test-device-1",
                "SerialNumber": "SERIAL-1",
                "ProductName": "iPhone",
                "OSVersion": "18.0",
            },
        )
        self.assertEqual(authenticate.status_code, 200)
        # Apple check-in acknowledgements use an empty HTTP response body.
        self.assertEqual(authenticate.data, b"")

        token_update = plist_request(
            self.client,
            "/checkin",
            {
                "MessageType": "TokenUpdate",
                "UDID": "test-device-1",
                "Token": b"fake-device-token",
                "PushMagic": "test-push-magic",
                "Topic": "com.apple.mgmt.External.test",
            },
        )
        self.assertEqual(token_update.status_code, 200)

        login = self.client.post("/api/admin/login", json={"token": "test-token"})
        self.assertEqual(login.status_code, 200)
        inventory = self.client.get("/api/devices")
        self.assertEqual(inventory.status_code, 200)
        device = inventory.get_json()["devices"][0]
        self.assertEqual(device["udid"], "test-device-1")
        self.assertEqual(device["last_status"], "enrolled")
        self.assertTrue(device["has_push_token"])

    def test_queue_command_requires_admin_and_mdm_returns_plist_command(self):
        checkin = plist_request(
            self.client,
            "/checkin",
            {
                "MessageType": "TokenUpdate",
                "UDID": "test-device-2",
                "Token": b"fake-device-token",
                "PushMagic": "test-push-magic",
                "Topic": "com.apple.mgmt.External.test",
            },
        )
        self.assertEqual(checkin.status_code, 200)

        denied = self.client.post(
            "/api/devices/test-device-2/commands",
            json={"command_type": "DeviceInformation", "payload": {}},
        )
        self.assertEqual(denied.status_code, 401)

        login = self.client.post("/api/admin/login", json={"token": "test-token"})
        self.assertEqual(login.status_code, 200)
        queued = self.client.post(
            "/api/devices/test-device-2/commands",
            json={"command_type": "DeviceInformation", "payload": {}},
        )
        self.assertEqual(queued.status_code, 202)
        self.assertIn("command_uuid", queued.get_json())

        command = plist_request(
            self.client,
            "/mdm",
            {"UDID": "test-device-2"},
        )
        self.assertEqual(command.status_code, 200)
        body = plistlib.loads(command.data)
        self.assertEqual(body["Command"]["RequestType"], "DeviceInformation")
        self.assertEqual(body["CommandUUID"], queued.get_json()["command_uuid"])

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

    def test_admin_login_rejects_invalid_token(self):
        response = self.client.post("/api/admin/login", json={"token": "wrong-token"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
