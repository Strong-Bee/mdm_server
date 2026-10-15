# iPhone Toolkit Local Helper

This helper runs on the Windows/macOS/Linux computer physically connected to the iPhone. Vercel hosts only the dashboard; it cannot access USB hardware directly.

## Features implemented

- `GET /health`: helper status.
- `GET /api/devices`: read-only USB discovery via `pymobiledevice3 usbmux list --usb`.
- `POST /api/firmware/inspect`: reads an uploaded IPSW archive and reports BuildManifest metadata, product/build versions, supported product types, component names, file size and SHA-256. It does not extract or modify firmware components.

No arbitrary command execution endpoint exists. The service binds to loopback by default.

## Install on Windows PowerShell

From the repository root:

```powershell
py -3.11 -m venv .venv-iphone
.\.venv-iphone\Scripts\Activate.ps1
python -m pip install -r device-helper\requirements.txt
$env:IPHONE_HELPER_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
$env:IPHONE_HELPER_ALLOWED_ORIGINS = "https://mdm-server-ten.vercel.app,https://mdm-server-git-feat-iphone-unified-toolkit-strongbees-projects.vercel.app,http://localhost:3000,http://127.0.0.1:3000"
python device-helper\app.py
```

Keep the token from the PowerShell session. It is printed only if the environment variable was omitted; prefer setting a persistent secret explicitly. The helper listens at `http://127.0.0.1:8787`.

Before testing, install Apple Devices or iTunes drivers, connect the iPhone by USB, unlock it, and tap **Trust This Computer**. Verify the CLI directly:

```powershell
pymobiledevice3 usbmux list --usb
```

The helper requires the same USB/usbmux access to work. For iOS 17+ developer services, pairing and a developer tunnel may be needed for additional commands; those commands are not exposed by this initial read-only helper.

## Connect the hosted dashboard

Open `/tools/lab` in the dashboard, set helper URL to `http://127.0.0.1:8787`, and enter the same helper token. Add the exact dashboard origin to `IPHONE_HELPER_ALLOWED_ORIGINS` if using another deployment URL, then restart the helper. Browser private-network restrictions may differ by browser; if the browser blocks the connection, use the local helper's documented endpoints from a local dashboard or configure a trusted HTTPS local reverse proxy. Do not expose this service directly to the public internet.

## IPSW inspection

Choose an official IPSW file in the dashboard and inspect metadata. The helper streams the file to a temporary local file, limits upload size using `IPHONE_HELPER_MAX_IPSW_BYTES` (default 16 GiB), reads only `BuildManifest.plist`, and deletes the temporary file. No firmware is uploaded to Vercel or the Flask MDM backend.

## Tests

```powershell
python -m pip install -r device-helper\requirements.txt
python -m unittest discover -s device-helper -p "test_*.py" -v
```

The tests mock the USB CLI. They verify API/auth behavior and IPSW parsing but do not prove that a physical iPhone is detected. Run `pymobiledevice3 usbmux list --usb` on the computer connected to your iPhone for a hardware test.
