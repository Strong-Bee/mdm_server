from apns2.client import APNsClient
from apns2.payload import Payload
from apns2.credentials import TokenCredentials
import sqlite3

def get_push_token(udid):
    conn = sqlite3.connect('mdm.db')
    cursor = conn.cursor()
    cursor.execute("SELECT push_token FROM devices WHERE udid = ?", (udid,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def send_apns_push(device_token, team_id, key_id, auth_key_path, topic):
    credentials = TokenCredentials(auth_key_path, team_id, key_id)
    client = APNsClient(credentials=credentials, use_sandbox=False)
    payload = Payload(content_available=True)
    client.send_notification(device_token, payload, topic)

def push_command_to_device(udid):
    token = get_push_token(udid)
    if token:
        send_apns_push(
            device_token=token,
            team_id="YOUR_TEAM_ID",
            key_id="YOUR_KEY_ID",
            auth_key_path="AuthKey_XXXXXX.p8",
            topic="com.apple.mgmt.External.YOUR_MDM_TOPIC"
        )
