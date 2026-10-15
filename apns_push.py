import base64
import os
import sqlite3

from apns2.client import APNsClient
from apns2.credentials import TokenCredentials
from apns2.payload import Payload


def _database_path():
    return os.environ.get(
        "MDM_DATABASE_PATH",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "mdm.db")),
    )


def get_device_push_details(udid):
    conn = sqlite3.connect(_database_path())
    try:
        row = conn.execute(
            "SELECT push_token, push_magic, push_topic FROM devices WHERE udid=?",
            (udid,),
        ).fetchone()
        return row
    finally:
        conn.close()


def send_apns_push(device_token, push_magic, team_id, key_id, auth_key_path, topic, use_sandbox=False):
    if not all([device_token, push_magic, team_id, key_id, auth_key_path, topic]):
        raise ValueError("APNs credentials, device token, PushMagic, and topic are required")

    credentials = TokenCredentials(auth_key_path, team_id, key_id)
    client = APNsClient(credentials=credentials, use_sandbox=use_sandbox)
    # Apple MDM push payload is {"mdm": PushMagic}; it is not an ordinary aps alert.
    payload = Payload(custom={"mdm": push_magic})
    client.send_notification(device_token, payload, topic)


def push_command_to_device(udid):
    details = get_device_push_details(udid)
    if not details or not details[0] or not details[1] or not details[2]:
        return False

    team_id = os.environ.get("APNS_TEAM_ID")
    key_id = os.environ.get("APNS_KEY_ID")
    auth_key_path = os.environ.get("APNS_AUTH_KEY_PATH")
    if not all([team_id, key_id, auth_key_path]):
        raise RuntimeError("Set APNS_TEAM_ID, APNS_KEY_ID, and APNS_AUTH_KEY_PATH")

    token = base64.b64decode(details[0])
    use_sandbox = os.environ.get("APNS_USE_SANDBOX", "false").lower() == "true"
    send_apns_push(
        device_token=token,
        push_magic=details[1],
        team_id=team_id,
        key_id=key_id,
        auth_key_path=auth_key_path,
        topic=details[2],
        use_sandbox=use_sandbox,
    )
    return True
