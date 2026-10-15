# tr4mpass companion integration: Apple MDM administration

This folder provides a small client for the separate [Apple MDM server](https://github.com/Strong-Bee/mdm_server). It is a **companion integration**, not a merge of MDM protocol code into the tr4mpass device/activation code.

## Scope and safety boundary

- Lists devices already known to the MDM server.
- Queues the non-destructive Apple `DeviceInformation` command for an enrolled device.
- Uses the MDM server's bearer-token admin API.
- Does not invoke DFU/exploit routines, alter activation records, remove Activation Lock, or attempt to enroll a device without authorization.
- Does not automatically enroll a device simply because a USB device was detected. USB detection and Apple MDM enrollment are different workflows.

The upstream tr4mpass repository is maintained by another owner, so this integration belongs in the companion MDM repository unless its owner explicitly accepts a change.

## Requirements

- Python 3.11+
- A running `Strong-Bee/mdm_server` instance.
- An already enrolled and authorized iPhone/iPad.
- `MDM_ADMIN_TOKEN` configured on the MDM server and set in your shell.

## Run

Set environment variables; do not hard-code or commit the token.

Linux/macOS:
```bash
export MDM_SERVER_URL="http://127.0.0.1:8000"
export MDM_ADMIN_TOKEN="your-admin-token"
python integrations/tr4mpass/mdm_client.py devices
python integrations/tr4mpass/mdm_client.py device-info "<ENROLLED-DEVICE-UDID>"
```

PowerShell:
```powershell
$env:MDM_SERVER_URL = "http://127.0.0.1:8000"
$env:MDM_ADMIN_TOKEN = "your-admin-token"
python .\integrations\tr4mpass\mdm_client.py devices
python .\integrations\tr4mpass\mdm_client.py device-info "<ENROLLED-DEVICE-UDID>"
```

HTTP is accepted only for localhost development. Use HTTPS for a remote MDM server. The client does not bypass TLS verification.

A successful command response means the command was queued and APNs notification was attempted; it does not prove the device received or executed it. Confirm the command result in the MDM server.

## Architecture

```
tr4mpass (USB detection / authorized device research)
          | manual operator hand-off only
          v
integrations/tr4mpass/mdm_client.py
          | HTTPS + MDM_ADMIN_TOKEN
          v
Strong-Bee/mdm_server
          | Apple MDM enrollment + APNs + command queue
          v
Previously enrolled iPhone/iPad
```

The MDM server remains experimental and must not be exposed publicly until its enrollment flow and device client-certificate identity validation are complete. See the MDM server README production-readiness checklist.
