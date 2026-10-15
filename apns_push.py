import base64
import os
import sqlite3
import time

import httpx
import jwt


def _database_path():
    return os.environ.get(
        "MDM_DATABASE_PATH",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "mdm.db")),
    )


def get_device_push_details(udid):
    conn = sqlite3.connect(_database_path())
    try:
        return conn.execute(
            "SELECT push_token, push_magic, push_topic FROM devices WHERE udid=?",
            (udid,),
        ).fetchone()
    finally:
        conn.close()


def send_apns_push(
    device_token,
    push_magic,
    team_id,
    key_id,
    auth_key_path,
    topic,
    use_sandbox=False,
):
    if not all([device_token, push_magic, team_id, key_id, auth_key_path, topic]):
        raise ValueError("APNs credentials, device token, PushMagic, and topic are required")
    if not topic.startswith("com.apple.mgmt."):
        raise ValueError("Apple MDM APNs topic must start with 'com.apple.mgmt.'")

    with open(auth_key_path, "r", encoding="utf-8") as key_file:
        private_key = key_file.read()

    auth_token = jwt.encode(
        {"iss": team_id, "iat": int(time.time())},
        private_key,
        algorithm="ES256",
        headers={"kid": key_id},
    )
    host = "https://api.sandbox.push.apple.com" if use_sandbox else "https://api.push.apple.com"
    url = f"{host}/3/device/{device_token.hex()}"
    headers = {
        "authorization": f"bearer {auth_token}",
        "apns-topic": topic,
        "apns-push-type": "mdm",
    }
    # Apple MDM uses only the custom mdm key, without an aps payload.
    with httpx.Client(http2=True, timeout=10.0) as client:
        response = client.post(url, headers=headers, json={"mdm": push_magic})
    if response.status_code != 200:
        reason = response.text[:500]
        raise RuntimeError(f"APNs returned HTTP {response.status_code}: {reason}")


def push_command_to_device(udid):
    details = get_device_push_details(udid)
    if not details or not details[0] or not details[1] or not details[2]:
        return False

    team_id = os.environ.get("APNS_TEAM_ID")
    key_id = os.environ.get("APNS_KEY_ID")
    auth_key_path = os.environ.get("APNS_AUTH_KEY_PATH")
    if not all([team_id, key_id, auth_key_path]):
        raise RuntimeError("Set APNS_TEAM_ID, APNS_KEY_ID, and APNS_AUTH_KEY_PATH")

    try:
        token = base64.b64decode(details[0], validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("Stored APNs device token is not valid base64") from exc

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
