"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { ApiError, DevicesResponse, MdmDevice, MdmCommandType, QueueCommandResponse } from "@/lib/mdm-types";
import { MDM_COMMANDS } from "@/lib/mdm-types";

type ViewState = "idle" | "loading" | "ready" | "error";

async function readJson<T>(response: Response): Promise<T> {
  const body = (await response.json().catch(() => ({}))) as T & ApiError;
  if (!response.ok) throw new Error(body.error || `Permintaan gagal (${response.status})`);
  return body;
}

function statusClass(status: string | null): string {
  const value = (status || "unknown").toLowerCase();
  if (value === "enrolled" || value === "authenticated") return "status status-good";
  if (value === "unenrolled") return "status status-muted";
  return "status";
}

export default function DashboardPage() {
  const [token, setToken] = useState("");
  const [tokenInput, setTokenInput] = useState("");
  const [devices, setDevices] = useState<MdmDevice[]>([]);
  const [viewState, setViewState] = useState<ViewState>("idle");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState("");
  const [commandType, setCommandType] = useState<MdmCommandType>("DeviceInformation");
  const [payloadText, setPayloadText] = useState("{}");
  const [queueBusy, setQueueBusy] = useState(false);

  const loadDevices = useCallback(async (authToken: string) => {
    setViewState("loading");
    setError("");
    try {
      const response = await fetch("/api/mdm/devices", {
        headers: { "x-mdm-admin-token": authToken },
        cache: "no-store",
      });
      const result = await readJson<DevicesResponse>(response);
      setDevices(result.devices);
      setViewState("ready");
    } catch (cause) {
      setViewState("error");
      setError(cause instanceof Error ? cause.message : "Gagal memuat perangkat.");
    }
  }, []);

  useEffect(() => {
    try {
      const stored = window.sessionStorage.getItem("mdm-admin-token");
      if (stored) {
        setToken(stored);
        setTokenInput(stored);
        void loadDevices(stored);
      }
    } catch {
      setError("Session storage tidak tersedia di browser ini.");
    }
  }, [loadDevices]);

  const filteredDevices = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return devices;
    return devices.filter((device) =>
      [device.udid, device.serial, device.product_name, device.os_version, device.last_status]
        .some((value) => value?.toLowerCase().includes(query)),
    );
  }, [devices, search]);

  async function connect(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const candidate = tokenInput.trim();
    if (candidate.length < 16) {
      setError("Masukkan token admin yang valid.");
      return;
    }
    setToken(candidate);
    try { window.sessionStorage.setItem("mdm-admin-token", candidate); } catch { /* Session-only fallback */ }
    await loadDevices(candidate);
  }

  function disconnect() {
    setToken("");
    setTokenInput("");
    setDevices([]);
    setViewState("idle");
    setNotice("");
    try { window.sessionStorage.removeItem("mdm-admin-token"); } catch { /* Ignore unavailable storage */ }
  }

  async function queueCommand(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selected) return;
    setQueueBusy(true);
    setError("");
    setNotice("");
    let payload: Record<string, unknown>;
    try {
      const parsed: unknown = JSON.parse(payloadText);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("Payload harus berupa objek JSON.");
      payload = parsed as Record<string, unknown>;
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Payload JSON tidak valid.");
      setQueueBusy(false);
      return;
    }
    try {
      const response = await fetch(`/api/mdm/devices/${encodeURIComponent(selected)}/commands`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-mdm-admin-token": token },
        body: JSON.stringify({ command_type: commandType, payload }),
      });
      const result = await readJson<QueueCommandResponse>(response);
      setNotice(`Perintah masuk antrean: ${result.command_uuid}. APNs: ${result.apns_notified ? "terkirim" : "belum terkonfirmasi"}.`);
      await loadDevices(token);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Gagal mengantrekan perintah.");
    } finally {
      setQueueBusy(false);
    }
  }

  return (
    <main className="dashboard-shell">
      <header className="dashboard-header">
        <a className="brand" href="/"><span className="brand-icon">⌘</span><span>mdm<span className="brand-muted">.server</span></span></a>
        <a className="dashboard-back" href="/">← Kembali ke landing page</a>
      </header>

      <section className="dashboard-intro">
        <div className="eyebrow"><span className="eyebrow-line" /> ADMINISTRASI PERANGKAT</div>
        <h1>Device <span>dashboard.</span></h1>
        <p>Panel TypeScript untuk membaca inventaris dan mengantrekan perintah melalui API backend MDM yang sudah dikonfigurasi.</p>
      </section>

      <section className="dashboard-panel">
        <div className="panel-heading"><div><h2>Koneksi backend</h2><p>Token admin hanya digunakan dari sesi browser ini.</p></div><span className={token ? "connection-state is-connected" : "connection-state"}>{token ? "TOKEN TERSIMPAN DI SESI" : "BELUM TERHUBUNG"}</span></div>
        <form className="token-form" onSubmit={connect}>
          <label htmlFor="admin-token">MDM admin token</label>
          <div className="token-row"><input id="admin-token" type="password" autoComplete="current-password" value={tokenInput} onChange={(event) => setTokenInput(event.target.value)} placeholder="Masukkan token admin" /><button className="button button-primary" type="submit" disabled={viewState === "loading"}>{viewState === "loading" ? "Menghubungkan…" : "Hubungkan"}</button>{token && <button className="button button-secondary" type="button" onClick={disconnect}>Putuskan</button>}</div>
          <small>Token disimpan di sessionStorage tab ini dan diteruskan melalui Next.js server route ke backend. Gunakan HTTPS dan jangan bagikan token.</small>
        </form>
      </section>

      {error && <div className="dashboard-alert alert-error" role="alert">{error}</div>}
      {notice && <div className="dashboard-alert alert-success" role="status">{notice}</div>}

      <section className="dashboard-panel">
        <div className="panel-heading"><div><h2>Inventaris perangkat</h2><p>{devices.length} perangkat terdaftar dalam respons backend</p></div><button className="button button-secondary" type="button" disabled={!token || viewState === "loading"} onClick={() => void loadDevices(token)}>↻ Refresh</button></div>
        <div className="device-toolbar"><input aria-label="Cari perangkat" placeholder="Cari UDID, serial, model, atau status…" value={search} onChange={(event) => setSearch(event.target.value)} /></div>
        {viewState === "idle" && <div className="empty-state">Masukkan token admin untuk memuat inventaris.</div>}
        {viewState === "loading" && <div className="empty-state">Memuat inventaris perangkat…</div>}
        {viewState === "error" && <div className="empty-state">Inventaris belum dapat dimuat. Periksa token dan konfigurasi backend.</div>}
        {viewState === "ready" && filteredDevices.length === 0 && <div className="empty-state">Tidak ada perangkat yang cocok dengan pencarian.</div>}
        {viewState === "ready" && filteredDevices.length > 0 && <div className="device-list">{filteredDevices.map((device) => <article className={selected === device.udid ? "device-row selected" : "device-row"} key={device.udid}><div className="device-summary"><div className="device-avatar">▯</div><div className="device-info"><strong>{device.product_name || "Apple device"}</strong><span>{device.serial || "Serial belum tersedia"}</span><code>{device.udid}</code></div></div><div className="device-meta"><span className={statusClass(device.last_status)}>{device.last_status || "unknown"}</span><span>{device.os_version || "OS —"}</span></div><button className="button button-secondary select-device" type="button" onClick={() => setSelected(device.udid)}>{selected === device.udid ? "Dipilih" : "Pilih"}</button></article>)}</div>}
      </section>

      <section className="dashboard-panel command-panel">
        <div className="panel-heading"><div><h2>Antrean perintah</h2><p>Pilih perangkat terdaftar dan perintah sesuai otorisasi.</p></div><span className="connection-state">MDM COMMANDS</span></div>
        <form className="command-form" onSubmit={queueCommand}>
          <label htmlFor="selected-device">Perangkat</label>
          <select id="selected-device" value={selected} onChange={(event) => setSelected(event.target.value)} required>
            <option value="">Pilih perangkat…</option>
            {devices.map((device) => <option key={device.udid} value={device.udid}>{device.product_name || "Apple device"} — {device.udid}</option>)}
          </select>
          <label htmlFor="command-type">Tipe perintah</label>
          <select id="command-type" value={commandType} onChange={(event) => setCommandType(event.target.value as MdmCommandType)}>
            {MDM_COMMANDS.map((command) => <option key={command} value={command}>{command}</option>)}
          </select>
          <label htmlFor="command-payload">Payload JSON</label>
          <textarea id="command-payload" rows={5} value={payloadText} onChange={(event) => setPayloadText(event.target.value)} spellCheck={false} />
          <p className="command-warning">Perintah sensitif seperti EraseDevice dapat menghapus data perangkat. Pastikan perangkat milik organisasi Anda dan ada persetujuan eksplisit sebelum mengirimkannya.</p>
          <button className="button button-primary" type="submit" disabled={!token || !selected || queueBusy}>{queueBusy ? "Mengantrekan…" : "Antrekan perintah"}</button>
        </form>
      </section>

      <footer className="dashboard-footer">MDM Server eksperimental · Gunakan hanya pada perangkat yang berizin. Status antrean/APNs bukan bukti bahwa perintah sudah dijalankan.</footer>
    </main>
  );
}
