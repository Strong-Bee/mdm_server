import hmac
import os
import sqlite3
import uuid
from functools import wraps

from flask import Blueprint, current_app, g, jsonify, request

mdm_bp = Blueprint("mdm", __name__)


def _connect():
    conn = sqlite3.connect(current_app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial TEXT,
            udid TEXT NOT NULL UNIQUE,
            ip TEXT,
            timestamp TEXT,
            al_bypass_code TEXT,
            push_token TEXT,
            last_status TEXT
        );
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            udid TEXT NOT NULL,
            command_uuid TEXT NOT NULL UNIQUE,
            command_type TEXT NOT NULL,
            payload TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


def _admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        expected = current_app.config.get("MDM_ADMIN_TOKEN") or os.environ.get("MDM_ADMIN_TOKEN")
        supplied = request.headers.get("Authorization", "")
        if not expected:
            return jsonify(error="Admin actions are disabled: MDM_ADMIN_TOKEN is not configured"), 503
        token = supplied[7:] if supplied.startswith("Bearer ") else ""
        if not token or not hmac.compare_digest(token, expected):
            return jsonify(error="Unauthorized"), 401
        return fn(*args, **kwargs)
    return wrapped


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
    return jsonify(status="ok", service="mdm-server"), 200


@mdm_bp.get("/api/devices")
@_admin_required
def list_devices():
    rows = g.mdm_db.execute(
        "SELECT id, serial, udid, ip, timestamp, last_status, "
        "CASE WHEN push_token IS NULL OR push_token = '' THEN 0 ELSE 1 END AS has_push_token "
        "FROM devices ORDER BY id DESC"
    ).fetchall()
    return jsonify(devices=[dict(row) for row in rows]), 200


@mdm_bp.post("/api/devices")
def register_device():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Request body must be a JSON object"), 400

    udid = data.get("udid")
    if not isinstance(udid, str) or not udid.strip() or len(udid.strip()) > 128:
        return jsonify(error="udid is required and must be at most 128 characters"), 400

    serial = data.get("serial")
    push_token = data.get("push_token")
    if serial is not None and (not isinstance(serial, str) or len(serial) > 64):
        return jsonify(error="serial must be a string of at most 64 characters"), 400
    if push_token is not None and (not isinstance(push_token, str) or len(push_token) > 512):
        return jsonify(error="push_token must be a string of at most 512 characters"), 400

    udid = udid.strip()
    try:
        g.mdm_db.execute(
            """INSERT INTO devices (serial, udid, ip, timestamp, push_token, last_status)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, 'registered')
               ON CONFLICT(udid) DO UPDATE SET
                 serial = COALESCE(excluded.serial, devices.serial),
                 ip = excluded.ip,
                 timestamp = CURRENT_TIMESTAMP,
                 push_token = COALESCE(excluded.push_token, devices.push_token),
                 last_status = 'registered'""",
            (serial, udid, request.remote_addr, push_token),
        )
        g.mdm_db.commit()
    except sqlite3.Error:
        current_app.logger.exception("Failed to register device")
        return jsonify(error="Could not register device"), 500

    return jsonify(status="registered", udid=udid), 201


@mdm_bp.post("/api/devices/<path:udid>/commands")
@_admin_required
def queue_command(udid):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Request body must be a JSON object"), 400

    command_type = data.get("command_type")
    allowed = {"DeviceInformation", "DeviceLock", "RestartDevice", "InstallProfile"}
    if command_type not in allowed:
        return jsonify(error="Unsupported command_type", allowed=sorted(allowed)), 400

    device = g.mdm_db.execute("SELECT 1 FROM devices WHERE udid = ?", (udid,)).fetchone()
    if device is None:
        return jsonify(error="Device not found"), 404

    payload = data.get("payload", {})
    if not isinstance(payload, dict):
        return jsonify(error="payload must be a JSON object"), 400

    command_uuid = str(uuid.uuid4())
    import json
    g.mdm_db.execute(
        "INSERT INTO commands (udid, command_uuid, command_type, payload, status) VALUES (?, ?, ?, ?, 'pending')",
        (udid, command_uuid, command_type, json.dumps(payload)),
    )
    g.mdm_db.commit()
    return jsonify(status="queued", command_uuid=command_uuid), 202
