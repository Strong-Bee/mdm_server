"use client";

import { useEffect, useState } from "react";

type Device = Record<string, string | number | boolean>;
type DeviceResponse = { devices?: Device[]; count?: number; error?: string; detail?: string; source?: string };
type FirmwareResult = {
  filename: string;
  size_bytes: number;
  sha256: string;
  product_version?: string;
  build_version?: string;
  supported_product_types: string[];
  build_identity_count: number;
  component_names: string[];
  archive_entry_count: number;
  inspection: string;
};
type ApiResult = DeviceResponse & { result?: FirmwareResult };

const panel: React.CSSProperties = {
  border: "1px solid var(--line, #263247)",
  borderRadius: "1rem",
  padding: "1.2rem",
};

function localHelperUrl(value: string): string {
  const url = new URL(value);
  const host = url.hostname.toLowerCase();
  if (!["localhost", "127.0.0.1", "::1", "[::1]"].includes(host)) {
    throw new Error("Untuk keamanan, helper hanya boleh di localhost/loopback.");
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error("URL helper harus menggunakan HTTP atau HTTPS.");
  }
  return url.toString().replace(/\/$/, "");
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  return `${(bytes / 1024 ** 3).toFixed(2)} GB`;
}

export default function IPhoneLabPage() {
  const [baseUrl, setBaseUrl] = useState("http://127.0.0.1:8787");
  const [token, setToken] = useState("");
  const [devices, setDevices] = useState<Device[]>([]);
  const [deviceState, setDeviceState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [firmware, setFirmware] = useState<FirmwareResult | null>(null);
  const [firmwareState, setFirmwareState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    try {
      const savedUrl = sessionStorage.getItem("iphone-helper-url");
      const savedToken = sessionStorage.getItem("iphone-helper-token");
      if (savedUrl) setBaseUrl(savedUrl);
      if (savedToken) setToken(savedToken);
    } catch {
      setError("Session storage tidak tersedia; masukkan konfigurasi secara manual.");
    }
  }, []);

  function saveSettings() {
    try {
      const normalized = localHelperUrl(baseUrl);
      sessionStorage.setItem("iphone-helper-url", normalized);
      sessionStorage.setItem("iphone-helper-token", token);
      setBaseUrl(normalized);
      setMessage("Konfigurasi disimpan hanya di sesi tab browser ini.");
      setError("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Konfigurasi tidak valid.");
    }
  }

  async function scanDevices() {
    setDeviceState("loading");
    setError("");
    setMessage("");
    try {
      const url = localHelperUrl(baseUrl);
      const response = await fetch(`${url}/api/devices`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      const result = (await response.json()) as DeviceResponse;
      if (!response.ok) throw new Error(result.error || `Helper mengembalikan HTTP ${response.status}`);
      setDevices(result.devices || []);
      setDeviceState("ready");
      setMessage(result.count ? `Ditemukan ${result.count} perangkat melalui ${result.source || "helper lokal"}.` : "Helper merespons, tetapi belum menemukan perangkat USB.");
      saveSettings();
    } catch (cause) {
      setDeviceState("error");
      setError(cause instanceof Error ? cause.message : "Tidak dapat terhubung ke helper lokal.");
    }
  }

  async function inspectFirmware(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const fileInput = form.elements.namedItem("ipsw") as HTMLInputElement | null;
    const file = fileInput?.files?.[0];
    if (!file) {
      setError("Pilih file IPSW terlebih dahulu.");
      return;
    }
    if (!file.name.toLowerCase().endsWith(".ipsw")) {
      setError("File harus berekstensi .ipsw.");
      return;
    }
    setFirmwareState("loading");
    setFirmware(null);
    setError("");
    setMessage("");
    try {
      const url = localHelperUrl(baseUrl);
      const data = new FormData();
      data.append("ipsw", file, file.name);
      const response = await fetch(`${url}/api/firmware/inspect`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: data,
      });
      const result = (await response.json()) as ApiResult;
      if (!response.ok) throw new Error(result.error || `Helper mengembalikan HTTP ${response.status}`);
      const firmwareResult = result as unknown as FirmwareResult;
      setFirmware(firmwareResult);
      setFirmwareState("ready");
      setMessage("Metadata IPSW berhasil dibaca oleh helper lokal. Komponen firmware tidak diekstrak atau dimodifikasi.");
      saveSettings();
    } catch (cause) {
      setFirmwareState("error");
      setError(cause instanceof Error ? cause.message : "Inspeksi IPSW gagal.");
    }
  }

  return (
    <main className="shell" style={{ paddingTop: "2rem", paddingBottom: "5rem" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", flexWrap: "wrap", marginBottom: "2rem" }}>
        <a className="brand" href="/tools"><span className="brand-icon">⌁</span><span>iPhone<span className="brand-muted">.toolkit</span></span></a>
        <a className="button button-secondary" href="/tools">← Kembali ke toolkit</a>
      </header>

      <section style={{ ...panel, marginBottom: "1rem", background: "linear-gradient(135deg, rgba(72,126,255,0.12), rgba(255,255,255,0.015))" }}>
        <p className="eyebrow">LOCAL DEVICE LAB</p>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 3rem)", margin: "0.4rem 0 0.8rem" }}>Hubungkan iPhone ke workspace.</h1>
        <p className="hero-description">Halaman ini berbicara langsung dari browser ke helper lokal di komputer yang terhubung USB. Dashboard Vercel tidak menerima file IPSW atau data USB secara langsung.</p>
      </section>

      {error && <div role="alert" style={{ ...panel, marginBottom: "1rem", borderColor: "#d66" }}><strong>Terjadi kesalahan</strong><p style={{ marginBottom: 0 }}>{error}</p></div>}
      {message && <div role="status" style={{ ...panel, marginBottom: "1rem" }}>{message}</div>}

      <section style={{ ...panel, marginBottom: "1rem" }}>
        <h2 style={{ marginTop: 0 }}>1. Konfigurasi helper lokal</h2>
        <label htmlFor="helper-url" style={{ display: "block", marginBottom: "0.4rem" }}>URL helper</label>
        <input id="helper-url" value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} spellCheck={false} placeholder="http://127.0.0.1:8787" style={{ width: "100%", boxSizing: "border-box", padding: "0.8rem", borderRadius: "0.65rem", border: "1px solid var(--line, #263247)", background: "transparent", color: "inherit", marginBottom: "0.8rem" }} />
        <label htmlFor="helper-token" style={{ display: "block", marginBottom: "0.4rem" }}>Token helper</label>
        <input id="helper-token" type="password" autoComplete="off" value={token} onChange={(event) => setToken(event.target.value)} placeholder="IPHONE_HELPER_TOKEN" style={{ width: "100%", boxSizing: "border-box", padding: "0.8rem", borderRadius: "0.65rem", border: "1px solid var(--line, #263247)", background: "transparent", color: "inherit", marginBottom: "0.8rem" }} />
        <div style={{ display: "flex", gap: "0.7rem", flexWrap: "wrap" }}>
          <button className="button button-secondary" type="button" onClick={saveSettings}>Simpan sesi</button>
          <button className="button button-primary" type="button" onClick={() => void scanDevices()} disabled={!token || deviceState === "loading"}>{deviceState === "loading" ? "Memindai USB…" : "Pindai perangkat USB"}</button>
        </div>
        <p style={{ opacity: 0.75, fontSize: "0.9rem", marginBottom: 0 }}>Jalankan helper dari folder <code>device-helper</code> di komputer. Pastikan iPhone tidak terkunci, kabel data terhubung, dan dialog “Trust This Computer” sudah disetujui.</p>
      </section>

      <section style={{ ...panel, marginBottom: "1rem" }}>
        <h2 style={{ marginTop: 0 }}>2. Hasil discovery perangkat</h2>
        {deviceState === "idle" && <p>Belum ada pemindaian. Tekan “Pindai perangkat USB” untuk memanggil pymobiledevice3.</p>}
        {deviceState === "loading" && <p>Menjalankan discovery USB dengan timeout 25 detik…</p>}
        {deviceState === "error" && <p>Discovery gagal. Periksa apakah helper berjalan, token benar, CORS diizinkan, dan driver Apple/usbmuxd tersedia.</p>}
        {deviceState === "ready" && devices.length === 0 && <p>Helper merespons tetapi tidak melihat iPhone. Periksa kabel data, Trust This Computer, Apple Devices/iTunes, dan jalankan <code>pymobiledevice3 usbmux list --usb</code> di komputer.</p>}
        {deviceState === "ready" && devices.length > 0 && <div style={{ display: "grid", gap: "0.7rem" }}>{devices.map((device, index) => <article key={String(device.udid || device.UniqueDeviceID || index)} style={{ border: "1px solid var(--line, #263247)", borderRadius: "0.7rem", padding: "0.8rem" }}><strong>{String(device.DeviceName || device.device_name || device.ProductType || device.product_type || "Apple device")}</strong><pre style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere", fontSize: "0.85rem" }}>{JSON.stringify(device, null, 2)}</pre></article>)}</div>}
      </section>

      <section style={panel}>
        <h2 style={{ marginTop: 0 }}>3. IPSW Inspector</h2>
        <p>Memeriksa metadata dari <code>BuildManifest.plist</code> dan menghitung SHA-256. File diproses oleh helper di komputer Anda; tidak dikirim ke backend MDM/Vercel. Komponen firmware tidak diekstrak atau dipatch.</p>
        <form onSubmit={inspectFirmware}>
          <label htmlFor="ipsw-file" style={{ display: "block", marginBottom: "0.4rem" }}>Pilih firmware IPSW</label>
          <input id="ipsw-file" name="ipsw" type="file" accept=".ipsw,application/octet-stream" required style={{ display: "block", width: "100%", marginBottom: "1rem" }} />
          <button className="button button-primary" type="submit" disabled={!token || firmwareState === "loading"}>{firmwareState === "loading" ? "Memeriksa metadata…" : "Inspeksi IPSW secara lokal"}</button>
        </form>
        {firmwareState === "error" && <p role="alert">Inspeksi gagal. Periksa format file dan batas ukuran helper.</p>}
        {firmware && <div style={{ marginTop: "1rem", borderTop: "1px solid var(--line, #263247)", paddingTop: "1rem" }}>
          <h3>Hasil firmware</h3>
          <dl style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 210px), 1fr))", gap: "0.8rem" }}>
            {[
              ["Nama file", firmware.filename],
              ["Ukuran", formatBytes(firmware.size_bytes)],
              ["Versi produk", firmware.product_version || "Tidak tersedia"],
              ["Build", firmware.build_version || "Tidak tersedia"],
              ["Build identities", String(firmware.build_identity_count)],
              ["Jumlah entri arsip", String(firmware.archive_entry_count)],
            ].map(([label, value]) => <div key={label}><dt style={{ opacity: 0.7, fontSize: "0.85rem" }}>{label}</dt><dd style={{ margin: "0.25rem 0", overflowWrap: "anywhere" }}>{value}</dd></div>)}
          </dl>
          <h4>Model yang didukung</h4>
          <p>{firmware.supported_product_types?.join(", ") || "Tidak tercantum"}</p>
          <h4>Komponen yang terdaftar (maks. 100)</h4>
          <p style={{ overflowWrap: "anywhere" }}>{firmware.component_names?.join(", ") || "Tidak tercantum"}</p>
          <h4>SHA-256</h4>
          <code style={{ overflowWrap: "anywhere" }}>{firmware.sha256}</code>
          <p style={{ opacity: 0.75, fontSize: "0.9rem" }}>{firmware.inspection}</p>
        </div>}
      </section>

      <aside style={{ ...panel, marginTop: "1rem" }}>
        <strong>Belum diimplementasikan</strong>
        <p style={{ marginBottom: 0 }}>Helper ini belum menjalankan jailbreak, eksploit DFU, modifikasi bootloader, atau operasi aktivasi. Modul selanjutnya dapat menambahkan pembacaan metadata perangkat yang lebih rinci dan analisis firmware offline setelah kompatibilitas tool dan OS diverifikasi.</p>
      </aside>
    </main>
  );
}
