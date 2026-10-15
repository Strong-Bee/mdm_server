"""Local-only, read-only helper for authorized iPhone diagnostics and IPSW inspection."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge

MAX_IPSW_BYTES = int(os.environ.get("IPHONE_HELPER_MAX_IPSW_BYTES", str(16 * 1024**3)))
MAX_MANIFEST_BYTES = 32 * 1024 * 1024
ALLOWED_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "IPHONE_HELPER_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,https://mdm-server-ten.vercel.app",
    ).split(",")
    if origin.strip()
}
TOKEN = os.environ.get("IPHONE_HELPER_TOKEN") or secrets.token_urlsafe(32)
if not os.environ.get("IPHONE_HELPER_TOKEN"):
    print(f"[iphone-helper] Generated one-time token for this process: {TOKEN}", flush=True)
    print("[iphone-helper] Set IPHONE_HELPER_TOKEN to a persistent secret before normal use.", flush=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_IPSW_BYTES + 1024 * 1024


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin", "").rstrip("/")
    if origin and origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Private-Network"] = "true"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.errorhandler(RequestEntityTooLarge)
def too_large(_error):
    return jsonify(error="File IPSW melebihi batas ukuran yang dikonfigurasi."), 413


@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    if request.method == "OPTIONS":
        return ("", 204)
    return jsonify(status="ok", service="iphone-local-helper", mode="read-only")


def authorized() -> bool:
    supplied = request.headers.get("Authorization", "")
    expected = f"Bearer {TOKEN}"
    return secrets.compare_digest(supplied, expected)


def require_auth():
    if not authorized():
        return jsonify(error="Token helper tidak valid. Atur IPHONE_HELPER_TOKEN dan masukkan token yang sama."), 401
    return None


@app.route("/api/devices", methods=["GET", "OPTIONS"])
def devices():
    if request.method == "OPTIONS":
        return ("", 204)
    denied = require_auth()
    if denied:
        return denied

    executable = shutil.which("pymobiledevice3")
    command = [executable, "usbmux", "list", "--usb"] if executable else [
        sys.executable, "-m", "pymobiledevice3", "usbmux", "list", "--usb"
    ]
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=25, check=False, shell=False
        )
    except subprocess.TimeoutExpired:
        return jsonify(error="Discovery USB timeout setelah 25 detik.", devices=[]), 504
    except OSError as exc:
        return jsonify(error=f"Tidak dapat menjalankan pymobiledevice3: {exc}", devices=[]), 503

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "Tidak ada detail").strip()[-1200:]
        return jsonify(
            error="Discovery USB gagal. Periksa instalasi pymobiledevice3, driver Apple/usbmuxd, kabel, dan izin Trust.",
            detail=detail,
            devices=[],
        ), 503

    try:
        parsed: Any = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError:
        return jsonify(error="Output CLI tidak berupa JSON yang dikenali.", detail=completed.stdout[-1200:], devices=[]), 502

    if isinstance(parsed, dict):
        parsed = [parsed]
    if not isinstance(parsed, list):
        return jsonify(error="Format daftar perangkat tidak dikenali.", devices=[]), 502

    safe_devices = []
    for item in parsed:
        if isinstance(item, str):
            safe_devices.append({"udid": item})
        elif isinstance(item, dict):
            safe = {}
            for key in ("udid", "UniqueDeviceID", "DeviceName", "device_name", "ProductType",
                        "product_type", "ProductVersion", "product_version", "SerialNumber",
                        "serial_number", "connection_type", "ConnectionType"):
                value = item.get(key)
                if isinstance(value, (str, int, float, bool)):
                    safe[key] = value
            if safe:
                safe_devices.append(safe)
    return jsonify(devices=safe_devices, count=len(safe_devices), source="pymobiledevice3 usbmux list --usb")


@app.route("/api/firmware/inspect", methods=["POST", "OPTIONS"])
def inspect_firmware():
    if request.method == "OPTIONS":
        return ("", 204)
    denied = require_auth()
    if denied:
        return denied
    uploaded = request.files.get("ipsw")
    if uploaded is None or not uploaded.filename:
        return jsonify(error="Pilih file .ipsw terlebih dahulu."), 400
    if Path(uploaded.filename).suffix.lower() != ".ipsw":
        return jsonify(error="Ekstensi file harus .ipsw."), 415

    digest = hashlib.sha256()
    total = 0
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="iphone-ipsw-", suffix=".ipsw", delete=False) as temp:
            temp_path = temp.name
            while True:
                chunk = uploaded.stream.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_IPSW_BYTES:
                    return jsonify(error=f"File melebihi batas {MAX_IPSW_BYTES} byte."), 413
                digest.update(chunk)
                temp.write(chunk)

        if total == 0:
            return jsonify(error="File IPSW kosong."), 400

        with zipfile.ZipFile(temp_path, "r") as archive:
            entries = archive.infolist()
            manifest_info = next((entry for entry in entries if entry.filename == "BuildManifest.plist"), None)
            if manifest_info is None:
                return jsonify(error="BuildManifest.plist tidak ditemukan; file mungkin bukan IPSW yang valid."), 422
            if manifest_info.file_size > MAX_MANIFEST_BYTES:
                return jsonify(error="BuildManifest.plist terlalu besar untuk inspeksi aman."), 422
            import plistlib
            manifest = plistlib.loads(archive.read(manifest_info))
            if not isinstance(manifest, dict):
                return jsonify(error="BuildManifest.plist tidak memiliki struktur dictionary."), 422

            identities = manifest.get("BuildIdentities", [])
            product_types = manifest.get("SupportedProductTypes", [])
            components = set()
            if isinstance(identities, list):
                for identity in identities:
                    if not isinstance(identity, dict):
                        continue
                    manifest_dict = identity.get("Manifest", {})
                    if isinstance(manifest_dict, dict):
                        components.update(str(name) for name in manifest_dict.keys())
            result = {
                "filename": Path(uploaded.filename).name,
                "size_bytes": total,
                "sha256": digest.hexdigest(),
                "product_version": manifest.get("ProductVersion"),
                "build_version": manifest.get("ProductBuildVersion"),
                "supported_product_types": product_types if isinstance(product_types, list) else [],
                "build_identity_count": len(identities) if isinstance(identities, list) else 0,
                "component_names": sorted(components)[:100],
                "archive_entry_count": len(entries),
                "inspection": "metadata-only; no firmware components extracted or modified",
            }
            return jsonify(result)
    except zipfile.BadZipFile:
        return jsonify(error="File bukan arsip ZIP/IPSW yang valid."), 422
    except (OSError, ValueError, KeyError) as exc:
        return jsonify(error=f"Gagal membaca metadata IPSW: {str(exc)[:500]}"), 422
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


@app.errorhandler(Exception)
def unexpected_error(error):
    # Avoid leaking stack traces, filesystem paths, or environment secrets to the client.
    app.logger.exception("Unhandled local-helper error")
    return jsonify(error="Kesalahan internal helper. Periksa log lokal."), 500


if __name__ == "__main__":
    host = os.environ.get("IPHONE_HELPER_HOST", "127.0.0.1")
    if host not in {"127.0.0.1", "::1", "localhost"} and os.environ.get("IPHONE_HELPER_ALLOW_REMOTE") != "1":
        raise SystemExit("Helper hanya boleh bind ke loopback. Set IPHONE_HELPER_ALLOW_REMOTE=1 hanya setelah mengamankan jaringan.")
    port = int(os.environ.get("IPHONE_HELPER_PORT", "8787"))
    app.run(host=host, port=port, debug=False, threaded=True)
