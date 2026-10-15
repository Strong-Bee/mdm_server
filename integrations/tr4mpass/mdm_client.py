#!/usr/bin/env python3
"""Small, read-only-first admin client for the Apple MDM server.

This utility does not perform activation, jailbreak, or Activation Lock changes.
It only lists devices and queues the non-destructive DeviceInformation command.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


def validate_base_url(value: str) -> str:
    parsed = urlparse(value)
    local_http = parsed.scheme == "http" and parsed.hostname in {
        "127.0.0.1", "localhost", "::1"
    }
    if parsed.scheme != "https" and not local_http:
        raise ValueError("MDM_SERVER_URL must use HTTPS (HTTP is allowed only for localhost).")
    if not parsed.netloc:
        raise ValueError("Invalid MDM server URL.")
    return value.rstrip("/")


def request_json(base_url: str, token: str, path: str, method: str = "GET",
                 payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = Request(base_url + path, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=15) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"MDM API returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach MDM server: {exc.reason}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("devices", "device-info"),
                        help="devices: list inventory; device-info: queue a non-destructive information request")
    parser.add_argument("udid", nargs="?", help="required for device-info")
    parser.add_argument("--base-url", default=os.environ.get(
        "MDM_SERVER_URL", "http://127.0.0.1:8000"),
        help="MDM server URL (or set MDM_SERVER_URL)")
    args = parser.parse_args()

    token = os.environ.get("MDM_ADMIN_TOKEN", "")
    if not token:
        print("Error: set MDM_ADMIN_TOKEN in the environment; never place it in source code.",
              file=sys.stderr)
        return 2
    if args.action == "device-info" and not args.udid:
        parser.error("device-info requires a UDID")

    try:
        base_url = validate_base_url(args.base_url)
        if args.action == "devices":
            result = request_json(base_url, token, "/api/devices")
        else:
            result = request_json(
                base_url, token,
                f"/api/devices/{quote(args.udid, safe='')}/commands",
                method="POST",
                payload={"command_type": "DeviceInformation", "payload": {}},
            )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
