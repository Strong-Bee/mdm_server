"use client";

import { useMemo, useState } from "react";

type Tool = {
  name: string;
  description: string;
  category: "diagnostics" | "firmware" | "boot" | "reference";
  url?: string;
  status: "reference" | "review";
};

const tools: Tool[] = [
  { name: "libimobiledevice", description: "Komunikasi perangkat, pairing, inventaris dan layanan iOS yang didukung.", category: "diagnostics", url: "https://github.com/libimobiledevice/libimobiledevice", status: "reference" },
  { name: "go-ios", description: "Utilitas perangkat iOS berbasis Go untuk alur diagnostik yang diotorisasi.", category: "diagnostics", url: "https://github.com/danielpaulus/go-ios", status: "reference" },
  { name: "pymobiledevice3", description: "Library Python untuk layanan perangkat dan riset protokol iOS.", category: "diagnostics", url: "https://github.com/doronz88/pymobiledevice3", status: "reference" },
  { name: "appium-ios-device", description: "Komunikasi perangkat untuk ekosistem otomasi Appium.", category: "diagnostics", url: "https://github.com/appium/appium-ios-device", status: "reference" },
  { name: "libideviceactivation", description: "Referensi protokol aktivasi; tidak digunakan untuk melewati kontrol aktivasi.", category: "diagnostics", url: "https://github.com/libimobiledevice/libideviceactivation", status: "reference" },
  { name: "img4tool", description: "Analisis kontainer firmware IMG4 secara offline.", category: "firmware", url: "https://github.com/tihmstar/img4tool", status: "reference" },
  { name: "iBoot64Patcher", description: "Referensi riset format dan bootloader tingkat rendah.", category: "firmware", url: "https://github.com/tihmstar/iBoot64Patcher", status: "reference" },
  { name: "ramdiskutil", description: "Referensi format dan utilitas ramdisk; tidak dieksekusi dari web.", category: "firmware", url: "https://github.com/verygenericname/ramdiskutil", status: "reference" },
  { name: "iExtractor", description: "Identitas repository upstream belum terverifikasi.", category: "firmware", status: "review" },
  { name: "gaster", description: "Referensi riset bootrom/checkm8; bukan aksi dashboard.", category: "boot", url: "https://github.com/0x7ff/gaster", status: "reference" },
  { name: "ipwndfu", description: "Referensi historis riset checkm8.", category: "boot", url: "https://github.com/axi0mX/ipwndfu", status: "reference" },
  { name: "checkra1n", description: "Proyek jailbreak eksternal, tidak dijalankan di server web.", category: "boot", url: "https://checkra.in/", status: "reference" },
  { name: "PongoOS", description: "Lingkungan pre-boot untuk riset perangkat yang kompatibel.", category: "boot", url: "https://github.com/checkra1n/PongoOS", status: "reference" },
  { name: "palera1n", description: "Tool jailbreak eksternal untuk perangkat/versi yang didukung.", category: "boot", url: "https://github.com/palera1n/palera1n", status: "reference" },
  { name: "jbinit", description: "Referensi boot dan ramdisk.", category: "boot", url: "https://github.com/verygenericname/jbinit", status: "reference" },
  { name: "Lockra1n", description: "URL, asal-usul dan lisensi perlu diverifikasi; tidak diintegrasikan.", category: "reference", status: "review" },
  { name: "LIBRE-HACKTIVATOR", description: "Referensi yang disebut terkait aktivasi; tidak diintegrasikan.", category: "reference", status: "review" },
  { name: "iOS-Hacktivation-Toolkit", description: "Referensi yang disebut terkait patch aktivasi; tidak diintegrasikan.", category: "reference", status: "review" },
  { name: "Onii_Ramdisk", description: "Referensi ramdisk yang belum diverifikasi; tidak diintegrasikan.", category: "reference", status: "review" },
];

const categories = [
  { id: "all", label: "Semua modul" },
  { id: "diagnostics", label: "Diagnostik" },
  { id: "firmware", label: "Firmware" },
  { id: "boot", label: "Boot & pre-boot" },
  { id: "reference", label: "Perlu review" },
] as const;

const modules = [
  { number: "01", title: "Device overview", description: "Discovery perangkat USB melalui pymobiledevice3 dari komputer lokal.", status: "Tersedia di /tools/lab; perlu helper lokal" },
  { number: "02", title: "Diagnostics", description: "Baca metadata lockdown iOS melalui koneksi USB yang telah dipercaya.", status: "Tersedia di /tools/lab; perlu helper lokal" },
  { number: "03", title: "IPSW inspector", description: "Baca BuildManifest, versi produk/build, model yang didukung, daftar komponen dan SHA-256.", status: "Metadata-only di /tools/lab; perlu helper lokal" },
  { number: "04", title: "Protocol library", description: "Indeks library upstream, dukungan platform, lisensi, dan status review.", status: "Katalog tersedia" },
];

const panel: React.CSSProperties = { border: "1px solid var(--line, #263247)", borderRadius: "1rem", padding: "1.15rem", background: "var(--card, rgba(255,255,255,0.02))" };

export default function ToolsPage() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<(typeof categories)[number]["id"]>("all");
  const filteredTools = useMemo(() => tools.filter((tool) => {
    const matchesCategory = category === "all" || (category === "reference" ? tool.status === "review" : tool.category === category);
    const needle = query.trim().toLowerCase();
    const matchesQuery = !needle || `${tool.name} ${tool.description}`.toLowerCase().includes(needle);
    return matchesCategory && matchesQuery;
  }), [category, query]);

  return (
    <main className="shell" style={{ paddingTop: "2rem", paddingBottom: "5rem" }}>
      <header style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "1rem", marginBottom: "2rem" }}>
        <a className="brand" href="/" aria-label="Kembali ke beranda">
          <span className="brand-icon" aria-hidden="true">⌁</span>
          <span>iPhone<span className="brand-muted">.toolkit</span></span>
        </a>
        <nav aria-label="Navigasi toolkit" style={{ display: "flex", flexWrap: "wrap", gap: "0.7rem" }}>
          <a className="button button-secondary" href="/">Beranda MDM</a>
          <a className="button button-primary" href="/tools/lab">Buka Device Lab ↗</a>
          <a className="button button-secondary" href="https://github.com/Strong-Bee/mdm_server/blob/main/device-helper/README.md" target="_blank" rel="noreferrer">Setup helper ↗</a>
        </nav>
      </header>

      <section style={{ ...panel, padding: "clamp(1.25rem, 4vw, 2.25rem)", marginBottom: "1.2rem", background: "linear-gradient(135deg, rgba(72,126,255,0.13), rgba(255,255,255,0.015))" }}>
        <p className="eyebrow">UNIFIED IPHONE WORKSPACE</p>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 3.4rem)", lineHeight: 1.05, margin: "0.5rem 0 1rem" }}>Satu workspace untuk<br />diagnostik dan riset iPhone.</h1>
        <p className="hero-description" style={{ maxWidth: "780px" }}>
          Satu antarmuka untuk katalog, discovery iPhone melalui helper lokal, dan inspeksi metadata IPSW offline. Discovery dan inspeksi memerlukan helper terpasang di komputer yang terhubung USB.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.65rem", marginTop: "1.25rem" }}>
          <span style={{ border: "1px solid var(--line, #263247)", borderRadius: "999px", padding: "0.4rem 0.7rem", fontSize: "0.85rem" }}>● UI aktif</span>
          <a className="button button-primary" href="/tools/lab">Buka Device Lab</a>
          <span style={{ border: "1px solid var(--line, #263247)", borderRadius: "999px", padding: "0.4rem 0.7rem", fontSize: "0.85rem" }}>Perangkat: belum dipindai</span>
          <span style={{ border: "1px solid var(--line, #263247)", borderRadius: "999px", padding: "0.4rem 0.7rem", fontSize: "0.85rem" }}>Helper lokal: perlu dijalankan</span>
        </div>
      </section>

      <section aria-label="Ringkasan workspace" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 165px), 1fr))", gap: "0.8rem", marginBottom: "2rem" }}>
        {[
          ["19", "referensi tercatat"],
          ["4", "modul workspace"],
          ["0", "tool native aktif"],
          ["Local-first", "arah arsitektur"],
        ].map(([value, label]) => <article key={label} style={panel}><p style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700 }}>{value}</p><p style={{ margin: "0.35rem 0 0", opacity: 0.72 }}>{label}</p></article>)}
      </section>

      <section style={{ marginBottom: "2.3rem" }}>
        <div style={{ marginBottom: "1rem" }}>
          <p className="eyebrow">WORKSPACE MODULES</p>
          <h2 style={{ margin: "0.3rem 0" }}>Pusat kerja iPhone</h2>
          <p style={{ marginTop: "0.4rem", opacity: 0.8 }}>Status ditampilkan secara eksplisit supaya rancangan UI tidak disalahartikan sebagai fungsi yang sudah berjalan.</p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 245px), 1fr))", gap: "0.9rem" }}>
          {modules.map((item) => <article key={item.number} style={panel}>
            <p style={{ margin: 0, opacity: 0.6 }}>{item.number} / MODULE</p>
            <h3 style={{ margin: "0.7rem 0 0.4rem" }}>{item.title}</h3>
            <p style={{ minHeight: "4.2em", opacity: 0.8 }}>{item.description}</p>
            <div style={{ borderTop: "1px solid var(--line, #263247)", paddingTop: "0.8rem", fontSize: "0.85rem" }}>Status: {item.status}</div>
          </article>)}
        </div>
      </section>

      <section style={{ marginBottom: "2rem" }}>
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "end", gap: "1rem", marginBottom: "1rem" }}>
          <div>
            <p className="eyebrow">OPEN-SOURCE INDEX</p>
            <h2 style={{ margin: "0.3rem 0" }}>Tool & library</h2>
            <p style={{ margin: 0, opacity: 0.75 }}>Cari dan filter semua referensi dalam satu tempat.</p>
          </div>
          <strong>{filteredTools.length} dari {tools.length} referensi</strong>
        </div>

        <label htmlFor="tool-search" style={{ display: "block", marginBottom: "0.5rem" }}>Cari tool</label>
        <input id="tool-search" type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Contoh: firmware, pairing, gaster..." style={{ width: "100%", padding: "0.85rem 1rem", borderRadius: "0.75rem", border: "1px solid var(--line, #263247)", background: "transparent", color: "inherit", marginBottom: "0.85rem" }} />
        <div role="group" aria-label="Filter kategori tool" style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "1rem" }}>
          {categories.map((item) => <button key={item.id} type="button" onClick={() => setCategory(item.id)} aria-pressed={category === item.id} className={category === item.id ? "button button-primary" : "button button-secondary"}>{item.label}</button>)}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 245px), 1fr))", gap: "0.8rem" }}>
          {filteredTools.map((tool) => <article key={tool.name} style={panel}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", gap: "0.5rem" }}>
              <h3 style={{ margin: 0, fontSize: "1.05rem" }}>{tool.name}</h3>
              <span style={{ fontSize: "0.72rem", opacity: 0.8, whiteSpace: "nowrap" }}>{tool.status === "review" ? "Perlu review" : "Referensi"}</span>
            </div>
            <p style={{ opacity: 0.78 }}>{tool.description}</p>
            {tool.url ? <a href={tool.url} target="_blank" rel="noreferrer">Repository upstream ↗</a> : <span style={{ opacity: 0.65 }}>URL upstream belum diverifikasi</span>}
          </article>)}
          {filteredTools.length === 0 && <p>Tidak ada tool yang cocok. Coba kata kunci atau kategori lain.</p>}
        </div>
      </section>

      <aside style={{ ...panel, borderColor: "rgba(230, 170, 60, 0.5)" }}>
        <h2 style={{ marginTop: 0 }}>Batasan implementasi</h2>
        <p style={{ marginBottom: "0.5rem" }}>Device Lab sekarang memiliki integrasi nyata ke helper lokal untuk discovery USB melalui pymobiledevice3 dan inspeksi metadata IPSW. Fitur ini baru dapat dipakai setelah helper dipasang dan dijalankan pada komputer yang terhubung ke iPhone.</p>
        <p style={{ marginBottom: 0 }}>Eksekusi native dari browser tetap tidak tersedia: helper lokal adalah proses terpisah dengan token dan CORS origin allowlist. IPSW dipindai metadata saja; tidak ada ekstraksi komponen atau patch firmware pada endpoint ini.</p>
      </aside>
    </main>
  );
}
