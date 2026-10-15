import base64
import hmac
import json
import os
import plistlib
import sqlite3
import uuid
from functools import wraps

from flask import Blueprint, current_app, g, jsonify, make_response, request, session

mdm_bp = Blueprint("mdm", __name__)
MDM_CONTENT_TYPE = "application/xml; charset=utf-8"


def _connect():
    conn = sqlite3.connect(current_app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT, serial TEXT, udid TEXT NOT NULL UNIQUE,
            ip TEXT, timestamp TEXT, al_bypass_code TEXT, push_token TEXT, last_status TEXT,
            push_magic TEXT, push_topic TEXT, product_name TEXT, os_version TEXT
        );
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT, udid TEXT NOT NULL, command_uuid TEXT NOT NULL UNIQUE,
            command_type TEXT NOT NULL, payload TEXT, status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, response TEXT
        );
    """)
    device_columns = {row["name"] for row in conn.execute("PRAGMA table_info(devices)")}
    for name, sql_type in {"last_status": "TEXT", "push_magic": "TEXT", "push_topic": "TEXT",
                           "product_name": "TEXT", "os_version": "TEXT"}.items():
        if name not in device_columns:
            conn.execute(f"ALTER TABLE devices ADD COLUMN {name} {sql_type}")
    command_columns = {row["name"] for row in conn.execute("PRAGMA table_info(commands)")}
    for name, sql_type in {"created_at": "TEXT", "response": "TEXT"}.items():
        if name not in command_columns:
            conn.execute(f"ALTER TABLE commands ADD COLUMN {name} {sql_type}")
    conn.commit()


def _admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        expected = current_app.config.get("MDM_ADMIN_TOKEN") or os.environ.get("MDM_ADMIN_TOKEN")
        if not expected:
            return jsonify(error="Admin actions are disabled: MDM_ADMIN_TOKEN is not configured"), 503
        supplied = request.headers.get("Authorization", "")
        token = supplied[7:] if supplied.startswith("Bearer ") else ""
        if not (bool(token) and hmac.compare_digest(token, expected)) and session.get("mdm_admin_authenticated") is not True:
            return jsonify(error="Unauthorized"), 401
        return fn(*args, **kwargs)
    return wrapped


def _plist_response(value=None, content_type=MDM_CONTENT_TYPE):
    response = make_response(b"" if value is None else plistlib.dumps(value, fmt=plistlib.FMT_XML, sort_keys=False), 200)
    response.headers["Content-Type"] = content_type
    return response


def _read_plist():
    try:
        value = plistlib.loads(request.get_data(cache=False))
    except (plistlib.InvalidFileException, ValueError, TypeError):
        return None
    return value if isinstance(value, dict) else None


def _update_device_from_checkin(message):
    udid = message.get("UDID")
    if not isinstance(udid, str) or not udid.strip():
        return False
    message_type = message.get("MessageType")
    token = message.get("Token")
    push_magic = message.get("PushMagic")
    topic = message.get("Topic")
    token_text = base64.b64encode(token).decode("ascii") if isinstance(token, bytes) else None
    serial = message.get("SerialNumber") if isinstance(message.get("SerialNumber"), str) else None
    product_name = message.get("ProductName") if isinstance(message.get("ProductName"), str) else None
    os_version = message.get("OSVersion") if isinstance(message.get("OSVersion"), str) else None

    if message_type == "TokenUpdate":
        if not token_text or not isinstance(push_magic, str) or not isinstance(topic, str):
            return False
        g.mdm_db.execute(
            """INSERT INTO devices (udid, serial, ip, timestamp, push_token, push_magic, push_topic,
                                    product_name, os_version, last_status)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, 'enrolled')
               ON CONFLICT(udid) DO UPDATE SET serial=COALESCE(excluded.serial, devices.serial),
                 ip=excluded.ip, timestamp=CURRENT_TIMESTAMP, push_token=excluded.push_token,
                 push_magic=excluded.push_magic, push_topic=excluded.push_topic,
                 product_name=COALESCE(excluded.product_name, devices.product_name),
                 os_version=COALESCE(excluded.os_version, devices.os_version), last_status='enrolled'""",
            (udid.strip(), serial, request.remote_addr, token_text, push_magic, topic, product_name, os_version),
        )
        g.mdm_db.commit()
        return True

    if message_type == "Authenticate":
        g.mdm_db.execute(
            """INSERT INTO devices (udid, serial, ip, timestamp, product_name, os_version, last_status)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, 'authenticated')
               ON CONFLICT(udid) DO UPDATE SET serial=COALESCE(excluded.serial, devices.serial),
                 ip=excluded.ip, timestamp=CURRENT_TIMESTAMP,
                 product_name=COALESCE(excluded.product_name, devices.product_name),
                 os_version=COALESCE(excluded.os_version, devices.os_version), last_status='authenticated'""",
            (udid.strip(), serial, request.remote_addr, product_name, os_version),
        )
        g.mdm_db.commit()
        return True

    if message_type == "CheckOut":
        g.mdm_db.execute("UPDATE devices SET last_status='unenrolled', timestamp=CURRENT_TIMESTAMP WHERE udid=?", (udid.strip(),))
        g.mdm_db.commit()
        return True
    return False


@mdm_bp.before_app_request
def open_database():
    g.mdm_db = _connect()
    _ensure_schema(g.mdm_db)


@mdm_bp.teardown_app_request
def close_database(exception=None):
    conn = g.pop("mdm_db", None)
    if conn is not None:
        conn.close()


@mdm_bp.get("/health")
def health():
    return jsonify(status="ok", service="apple-ios-mdm"), 200


@mdm_bp.post("/checkin")
@mdm_bp.put("/checkin")
def apple_checkin():
    message = _read_plist()
    if message is None:
        return jsonify(error="Expected an Apple MDM plist request"), 400
    if not _update_device_from_checkin(message):
        return jsonify(error="Invalid or unsupported MDM check-in message"), 400
    return _plist_response()


@mdm_bp.put("/mdm")
def apple_mdm_connect():
    message = _read_plist()
    if message is None:
        return jsonify(error="Expected an Apple MDM plist request"), 400
    udid, status, command_uuid = message.get("UDID"), message.get("Status"), message.get("CommandUUID")
    if not isinstance(udid, str) or not udid.strip():
        return jsonify(error="Missing UDID"), 400

    if isinstance(command_uuid, str) and isinstance(status, str):
        response_json = json.dumps(message, default=lambda value: base64.b64encode(value).decode("ascii"))
        g.mdm_db.execute("UPDATE commands SET status=?, response=? WHERE command_uuid=? AND udid=?",
                         (status, response_json, command_uuid, udid))
        g.mdm_db.execute("UPDATE devices SET last_status=?, timestamp=CURRENT_TIMESTAMP WHERE udid=?", (status, udid))
        g.mdm_db.commit()

    row = g.mdm_db.execute(
        "SELECT id, command_uuid, command_type, payload FROM commands WHERE udid=? AND status='pending' ORDER BY id ASC LIMIT 1",
        (udid,),
    ).fetchone()
    if row is None:
        return _plist_response()
    try:
        payload = json.loads(row["payload"] or "{}")
    except json.JSONDecodeError:
        current_app.logger.exception("Invalid stored command payload")
        return _plist_response()
    if not isinstance(payload, dict):
        return _plist_response()
    command = {"RequestType": row["command_type"], **payload}
    g.mdm_db.execute("UPDATE commands SET status='sent' WHERE id=? AND status='pending'", (row["id"],))
    g.mdm_db.commit()
    return _plist_response({"CommandUUID": row["command_uuid"], "Command": command})


@mdm_bp.get("/api/devices")
@_admin_required
def list_devices():
    rows = g.mdm_db.execute(
        """SELECT id, serial, udid, ip, timestamp, last_status, product_name, os_version, push_topic,
                  CASE WHEN push_token IS NULL OR push_token='' THEN 0 ELSE 1 END AS has_push_token
           FROM devices ORDER BY id DESC"""
    ).fetchall()
    return jsonify(devices=[dict(row) for row in rows]), 200


@mdm_bp.post("/api/devices/<path:udid>/commands")
@_admin_required
def queue_command(udid):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Request body must be a JSON object"), 400
    allowed = {"DeviceInformation", "DeviceLock", "EraseDevice", "RestartDevice", "InstallProfile", "ProfileList", "InstalledApplicationList"}
    command_type = data.get("command_type")
    if command_type not in allowed:
        return jsonify(error="Unsupported Apple MDM RequestType", allowed=sorted(allowed)), 400
    device = g.mdm_db.execute("SELECT 1 FROM devices WHERE udid=?", (udid,)).fetchone()
    if device is None:
        return jsonify(error="Device not found"), 404
    payload = data.get("payload", {})
    if not isinstance(payload, dict):
        return jsonify(error="payload must be an object matching Apple's command schema"), 400
    command_uuid = str(uuid.uuid4()).upper()
    g.mdm_db.execute(
        "INSERT INTO commands (udid, command_uuid, command_type, payload, status) VALUES (?, ?, ?, ?, 'pending')",
        (udid, command_uuid, command_type, json.dumps(payload)),
    )
    g.mdm_db.commit()
    try:
        from apns_push import push_command_to_device
        pushed = push_command_to_device(udid)
    except Exception:
        current_app.logger.exception("Command queued, but APNs notification failed for device %s", udid)
        pushed = False
    return jsonify(status="queued", command_uuid=command_uuid, apns_notified=bool(pushed)), 202
