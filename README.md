# Apple iOS/iPadOS MDM Server

A Python/Flask implementation baseline for experimenting with Apple's Mobile Device Management (MDM) protocol for **authorized iPhone and iPad administration**.

> **Status: experimental — not production-ready.** This repository is not a complete Apple MDM product. Do not expose it to the public internet or enroll real devices until enrollment trust, TLS, authorization, command validation, and end-to-end testing are complete.

## Scope

The project is intended for Apple iOS/iPadOS devices and includes an initial implementation of:

- Apple plist-based check-in handling for `Authenticate`, `TokenUpdate`, and `CheckOut`.
- An MDM command connection endpoint that returns queued commands as plist responses.
- SQLite storage for device identifiers, enrollment/push metadata, basic inventory fields, and command status.
- APNs MDM push notification support using environment-provided credentials.
- Token-protected administrative API endpoints.
- Basic Python unit tests and GitHub Actions CI.

### Important limitations

This is a protocol baseline, not a production-complete MDM server. In particular:

- Enrollment profile generation/signing and verification are not implemented as a complete enrollment workflow.
- Device identity and MDM client-certificate validation must be implemented and verified at the TLS/reverse-proxy boundary before public deployment.
- Apple command payloads and responses need complete schema validation and broader protocol coverage.
- APNs behavior needs integration testing with valid Apple-issued credentials and an enrolled device.
- The current tests are smoke tests; they do not replace end-to-end testing on a real iPhone/iPad.
- Activation Lock bypass is **not implemented** and is not promised by this project.

## Architecture

Typical Apple MDM communication has two distinct paths:

1. **Check-in service** — the device reports enrollment/check-in messages to `/checkin`.
2. **MDM command service** — APNs wakes the device; the device connects to `/mdm` to retrieve queued commands and report their results.

APNs is a wake-up signal, not the channel that carries the command payload itself. The device connects to the MDM server to fetch commands.

## Requirements

- Python 3.11 or later (CI currently targets Python 3.11).
- Dependencies from `requirements.txt`.
- A persistent writable directory for the SQLite database.
- For real device push notifications: valid Apple MDM/APNs configuration and credentials.
- HTTPS with a valid certificate for any device-facing deployment.

## Local setup

### 1. Clone and install

```bash
git clone https://github.com/Strong-Bee/mdm_server.git
cd mdm_server
python -m venv .venv
```

Activate the environment:

**Linux/macOS**
```bash
source .venv/bin/activate
```

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### 2. Configure environment variables

Set a unique, strong secret and an administrative token. Do not commit real secrets to Git.

**Linux/macOS**
```bash
export FLASK_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export MDM_ADMIN_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export MDM_DATABASE_PATH="$PWD/mdm.db"
export MDM_HOST="127.0.0.1"
export PORT="8000"
```

**Windows PowerShell**
```powershell
$env:FLASK_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
$env:MDM_ADMIN_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
$env:MDM_DATABASE_PATH = "$PWD\mdm.db"
$env:MDM_HOST = "127.0.0.1"
$env:PORT = "8000"
```

For APNs, configure the values required by `apns_push.py`:

- `APNS_TEAM_ID`
- `APNS_KEY_ID`
- `APNS_AUTH_KEY_PATH` — path to the Apple-issued APNs authentication key file
- `APNS_USE_SANDBOX` — `true` only when the environment and token are configured for the APNs sandbox; otherwise `false`

Keep the APNs key outside the repository and restrict file permissions. APNs credentials and device tokens must be handled as secrets.

### 3. Start the server

```bash
python main.py
```

The default bind address is `127.0.0.1:8000`. This is intentionally local-only by default. Do not bind to a public interface until TLS, device identity checks, and deployment controls are configured.

Optional TLS settings for local/testing use:

- `SSL_CERT_FILE`
- `SSL_KEY_FILE`

Both must point to existing files to enable the built-in TLS context. For production, use a properly configured HTTPS reverse proxy and implement the required Apple MDM client identity validation.

### 4. Check health

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "apple-ios-mdm"
}
```

The health endpoint confirms only that the Flask app responds; it does not verify Apple enrollment or APNs connectivity.

## Current endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Basic service health check |
| POST / PUT | `/checkin` | Accept supported Apple MDM plist check-in messages |
| PUT | `/mdm` | Receive device MDM requests/responses and return a pending command when available |
| POST | `/api/admin/login` | Start an administrative session using `MDM_ADMIN_TOKEN` |
| POST | `/api/admin/logout` | Clear the administrative session |
| GET | `/api/devices` | List device inventory; requires admin authentication |
| POST | `/api/devices/<udid>/commands` | Queue an allowed MDM command; requires admin authentication |

The check-in and MDM endpoints expect Apple plist request bodies, not arbitrary JSON. Device-facing endpoints are not safe to expose publicly until enrollment and device identity validation are in place.

### Administrative API example

List devices using a bearer token:

```bash
curl -H "Authorization: Bearer $MDM_ADMIN_TOKEN" \
  http://127.0.0.1:8000/api/devices
```

Queue a basic device-information request for an already enrolled device:

```bash
curl -X POST \
  -H "Authorization: Bearer $MDM_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command_type":"DeviceInformation","payload":{}}' \
  "http://127.0.0.1:8000/api/devices/<UDID>/commands"
```

Replace `<UDID>` with the enrolled device's UDID. The API reports whether the APNs notification was sent; successful queuing or notification does **not** guarantee that the device executed the command. Check the command response/status and device logs.

Only use commands on devices you own or are explicitly authorized to manage. Commands such as `EraseDevice` are destructive and should be handled with additional confirmation and audit controls before production use.

## Database

The default SQLite database is `mdm.db` in the project directory. Set `MDM_DATABASE_PATH` to use a different location. Back up the database before testing schema changes or running migrations. The current schema stores sensitive device and push metadata; protect the database file and its backups.

## Tests

Install dependencies, then run:

```bash
python -m compileall -q app main.py apns_push.py tests
python -m unittest discover -s tests -v
```

GitHub Actions runs Python compilation and unit tests on pushes to `main` and `fix/**`, and on pull requests targeting `main`. Review the latest CI run before merging.

## Production readiness checklist

- [ ] Complete signed enrollment-profile workflow and verify profile installation/enrollment.
- [ ] Enforce HTTPS and validate device identity/client certificates according to Apple's MDM requirements.
- [ ] Protect enrollment/check-in endpoints against spoofing and unauthorized requests.
- [ ] Validate every supported command and response against Apple's protocol schema.
- [ ] Verify APNs topic, PushMagic, device token, and credentials with a real enrolled test device.
- [ ] Add audit logs, rate limits, monitoring, backups, and retention controls.
- [ ] Add end-to-end tests for enrollment, TokenUpdate, command delivery, command results, and CheckOut.
- [ ] Review destructive-command permissions and require explicit confirmation.
- [ ] Rotate all secrets and restrict access to the database and APNs key.

## References

- [Apple Device Management documentation](https://developer.apple.com/documentation/devicemanagement)
- [Apple MDM Check-in](https://developer.apple.com/documentation/devicemanagement/check-in)
- [Sending MDM Commands to a Device](https://developer.apple.com/documentation/devicemanagement/sending-mdm-commands-to-a-device)

## License

Check the repository's license file before redistributing or using this project in a commercial product.
