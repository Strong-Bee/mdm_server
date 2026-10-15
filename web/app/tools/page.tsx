const groups = [
  {
    title: "Komunikasi dan diagnostik perangkat",
    description: "Referensi untuk inventaris, pairing, dan layanan perangkat yang diotorisasi.",
    tools: [
      ["libimobiledevice", "Komunikasi perangkat iOS", "https://github.com/libimobiledevice/libimobiledevice"],
      ["go-ios", "Utilitas perangkat berbasis Go", "https://github.com/danielpaulus/go-ios"],
      ["pymobiledevice3", "Library Python untuk layanan iOS", "https://github.com/doronz88/pymobiledevice3"],
      ["appium-ios-device", "Library Node.js ekosistem Appium", "https://github.com/appium/appium-ios-device"],
      ["libideviceactivation", "Referensi library aktivasi perangkat", "https://github.com/libimobiledevice/libideviceactivation"],
    ],
  },
  {
    title: "Analisis firmware",
    description: "Referensi untuk pemeriksaan firmware offline; bukan layanan pemrosesan firmware jarak jauh.",
    tools: [
      ["img4tool", "Kontainer firmware IMG4", "https://github.com/tihmstar/img4tool"],
      ["iBoot64Patcher", "Riset bootloader tingkat rendah", "https://github.com/tihmstar/iBoot64Patcher"],
      ["ramdiskutil", "Referensi utilitas ramdisk", "https://github.com/verygenericname/ramdiskutil"],
      ["iExtractor", "Sumber upstream perlu diverifikasi", "https://github.com"],
    ],
  },
  {
    title: "Riset bootrom dan pre-boot",
    description: "Hanya katalog referensi riset. Tool ini tidak dijalankan dari dashboard atau backend MDM.",
    tools: [
      ["gaster", "Riset bootrom/checkm8", "https://github.com/0x7ff/gaster"],
      ["ipwndfu", "Referensi historis checkm8", "https://github.com/axi0mX/ipwndfu"],
      ["checkra1n", "Riset jailbreak", "https://checkra.in/"],
      ["PongoOS", "Lingkungan pre-boot riset", "https://github.com/checkra1n/PongoOS"],
      ["palera1n", "Riset jailbreak perangkat tertentu", "https://github.com/palera1n/palera1n"],
      ["jbinit", "Referensi boot/ramdisk", "https://github.com/verygenericname/jbinit"],
    ],
  },
  {
    title: "Referensi yang belum diverifikasi",
    description: "Nama dan URL kanonis belum diverifikasi. Tidak dipasang atau dieksekusi oleh aplikasi ini.",
    tools: [
      ["Lockra1n", "Provenance/URL perlu verifikasi", ""],
      ["LIBRE-HACKTIVATOR", "Provenance/URL perlu verifikasi", ""],
      ["iOS-Hacktivation-Toolkit", "Provenance/URL perlu verifikasi", ""],
      ["Onii_Ramdisk", "Provenance/URL perlu verifikasi", ""],
    ],
  },
];

export default function ToolsPage() {
  return (
    <main className="shell" style={{ paddingTop: "3rem", paddingBottom: "5rem" }}>
      <header style={{ maxWidth: "850px", marginBottom: "2.5rem" }}>
        <p className="eyebrow">APPLE DEVICE MANAGEMENT</p>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 3.5rem)", lineHeight: 1.08 }}>
          Katalog tool riset iOS
        </h1>
        <p className="hero-description">
          Indeks referensi open-source untuk diagnostik perangkat, komunikasi layanan,
          dan analisis firmware. Entri katalog bukan berarti tool telah dipasang,
          diuji, atau dijalankan oleh server ini.
        </p>
        <p>
          <a className="button button-secondary" href="/">Kembali ke beranda</a>{" "}
          <a className="button button-primary" href="https://github.com/Strong-Bee/mdm_server/blob/main/docs/IOS-RESEARCH-TOOLS.md" target="_blank" rel="noreferrer">
            Dokumentasi lengkap
          </a>
        </p>
      </header>

      <div style={{ border: "1px solid var(--line, #263247)", borderRadius: "1rem", padding: "1rem 1.25rem", marginBottom: "2rem" }}>
        <strong>Catatan keamanan</strong>
        <p style={{ marginBottom: 0 }}>
          Halaman ini hanya katalog referensi. Tidak menyediakan eksekusi exploit,
          bypass Activation Lock, penghapusan status aktivasi, atau patch layanan aktivasi.
          Jangan gunakan tool terhadap perangkat yang tidak Anda miliki atau tidak Anda kelola dengan izin.
        </p>
      </div>

      <div style={{ display: "grid", gap: "1.5rem" }}>
        {groups.map((group) => (
          <section key={group.title} style={{ border: "1px solid var(--line, #263247)", borderRadius: "1rem", padding: "1.25rem" }}>
            <h2 style={{ fontSize: "1.35rem", marginTop: 0 }}>{group.title}</h2>
            <p>{group.description}</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 250px), 1fr))", gap: "0.8rem" }}>
              {group.tools.map(([name, description, url]) => (
                <article key={name} style={{ border: "1px solid var(--line, #263247)", borderRadius: "0.75rem", padding: "1rem" }}>
                  <h3 style={{ marginTop: 0, marginBottom: "0.4rem", fontSize: "1.05rem" }}>{name}</h3>
                  <p style={{ marginTop: 0 }}>{description}</p>
                  {url ? (
                    <a href={url} target="_blank" rel="noreferrer">Buka sumber ↗</a>
                  ) : (
                    <span>URL belum diverifikasi</span>
                  )}
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>

      <p style={{ marginTop: "2rem", opacity: 0.8 }}>
        Status: katalog dokumentasi. Belum ada executable tool yang diinstal oleh halaman ini.
      </p>
    </main>
  );
}
