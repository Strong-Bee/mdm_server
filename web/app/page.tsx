const repositoryUrl = "https://github.com/Strong-Bee/mdm_server";
const readmeUrl = `${repositoryUrl}/blob/main/README.md`;

function Mark({ children }: { children: React.ReactNode }) {
  return <span className="mark">{children}</span>;
}

function ArrowIcon() {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true">
      <path d="M4.2 10h11.2M10 4.7l5.4 5.3-5.4 5.3" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3 19 6v5.2c0 4.5-2.8 7.7-7 9.8-4.2-2.1-7-5.3-7-9.8V6l7-3Z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}

function DeviceIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="6" y="2.5" width="12" height="19" rx="2.2" />
      <path d="M10 5h4M10.5 18.5h3" />
    </svg>
  );
}

function PulseIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 12h4l2.3-6 4.2 12 2.4-6H21" />
    </svg>
  );
}

const capabilities = [
  {
    number: "01",
    title: "Check-in perangkat",
    description:
      "Menerima pesan plist yang didukung seperti Authenticate, TokenUpdate, dan CheckOut.",
    icon: <DeviceIcon />,
  },
  {
    number: "02",
    title: "Antrean perintah MDM",
    description:
      "Fondasi alur antrean perintah dan respons perangkat melalui endpoint MDM.",
    icon: <PulseIcon />,
  },
  {
    number: "03",
    title: "Push melalui APNs",
    description:
      "Mengirim sinyal wake-up APNs agar perangkat mengambil perintah dari server.",
    icon: <ArrowIcon />,
  },
  {
    number: "04",
    title: "Inventaris dasar",
    description:
      "Menyimpan metadata perangkat dan status perintah pada basis data SQLite.",
    icon: <ShieldIcon />,
  },
];

const flow = [
  ["01", "Perangkat", "Mengirim check-in plist"],
  ["02", "Server MDM", "Menyimpan metadata perangkat"],
  ["03", "Admin berwenang", "Mengantrekan perintah yang diizinkan"],
  ["04", "APNs + perangkat", "Wake-up, ambil perintah, lalu kirim status"],
];

export default function Home() {
  return (
    <main>
      <div className="announcement">
        <span className="announcement-dot" />
        Proyek open source eksperimental
        <a href={readmeUrl}>Baca dokumentasi <ArrowIcon /></a>
      </div>

      <header className="site-header shell">
        <a className="brand" href="#top" aria-label="Apple MDM Server beranda">
          <span className="brand-icon"><ShieldIcon /></span>
          <span>mdm<span className="brand-muted">.server</span></span>
        </a>
        <nav className="nav-links" aria-label="Navigasi utama">
          <a href="#fitur">Fitur</a>
          <a href="#alur">Cara kerja</a>
          <a href="/dashboard">Dashboard</a>
          <a href="#keamanan">Keamanan</a>
        </nav>
        <a className="header-cta" href={repositoryUrl} target="_blank" rel="noreferrer">
          Lihat GitHub <ArrowIcon />
        </a>
      </header>

      <section className="hero shell" id="top">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-line" /> APPLE DEVICE MANAGEMENT</div>
          <h1>Memahami MDM.<br /><span>Membangun dengan</span><br />lebih terarah.</h1>
          <p className="hero-description">
            Fondasi eksperimental server Mobile Device Management untuk iPhone
            dan iPad. Pelajari alur protokol, antrean perintah, dan notifikasi
            APNs dalam satu proyek yang terbuka dan terdokumentasi.
          </p>
          <div className="hero-actions">
            <a className="button button-primary" href={repositoryUrl} target="_blank" rel="noreferrer">
              Jelajahi repository <ArrowIcon />
            </a>
            <a className="button button-secondary" href="#alur">Pelajari alurnya</a>
          </div>
          <div className="hero-footnote">
            <span className="status-dot" />
            <span>Python · Flask · SQLite · Apple MDM protocol</span>
          </div>
        </div>

        <div className="hero-visual" aria-label="Ilustrasi alur perangkat ke server MDM">
          <div className="visual-glow" />
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="device-card">
            <div className="device-speaker" />
            <div className="device-screen">
              <div className="screen-top"><span>DEVICE STATUS</span><span className="live-pill">TEST</span></div>
              <div className="phone-glyph"><DeviceIcon /></div>
              <div className="screen-title">iOS / iPadOS</div>
              <div className="screen-subtitle">Managed device flow</div>
              <div className="screen-divider" />
              <div className="screen-row"><span>Check-in</span><span className="screen-value">Plist</span></div>
              <div className="screen-row"><span>Command</span><span className="screen-value">Queued</span></div>
              <div className="screen-row"><span>Push</span><span className="screen-value">APNs</span></div>
            </div>
          </div>
          <div className="server-card">
            <div className="server-icon"><ShieldIcon /></div>
            <div><strong>MDM Server</strong><span>Flask API</span></div>
            <span className="server-indicator" />
          </div>
          <div className="connection connection-top"><span /></div>
          <div className="connection connection-bottom"><span /></div>
          <div className="floating-tag tag-checkin"><span className="tag-icon">↘</span><span><b>Check-in</b><small>Device identity flow</small></span></div>
          <div className="floating-tag tag-command"><span className="tag-icon">⌁</span><span><b>Command queue</b><small>Response tracking</small></span></div>
          <div className="visual-caption"><span className="caption-bars">▥</span> PROTOCOL FLOW <span>•</span> CONCEPTUAL VIEW</div>
        </div>
      </section>

      <section className="trust-strip shell" aria-label="Ringkasan teknologi">
        <div><span className="trust-label">DIBANGUN DENGAN</span><strong>Python + Flask</strong></div>
        <span className="trust-separator" />
        <div><span className="trust-label">PENYIMPANAN</span><strong>SQLite</strong></div>
        <span className="trust-separator" />
        <div><span className="trust-label">NOTIFIKASI</span><strong>Apple Push Notification service</strong></div>
        <span className="trust-separator" />
        <div><span className="trust-label">STATUS PROYEK</span><strong><span className="mini-status" /> Eksperimental</strong></div>
      </section>

      <section className="section shell" id="fitur">
        <div className="section-heading">
          <div>
            <div className="eyebrow"><span className="eyebrow-line" /> KOMPONEN UTAMA</div>
            <h2>Fondasi yang mudah<br />dipelajari dan diperluas.</h2>
          </div>
          <p>Mulai dari alur protokol inti dengan batasan yang dijelaskan secara terbuka. Bukan klaim sebagai platform MDM siap produksi.</p>
        </div>
        <div className="feature-grid">
          {capabilities.map((item) => (
            <article className="feature-card" key={item.number}>
              <div className="feature-top"><span className="feature-icon">{item.icon}</span><span className="feature-number">{item.number}</span></div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
              <span className="feature-rule" />
            </article>
          ))}
        </div>
      </section>

      <section className="workflow-section" id="alur">
        <div className="shell workflow-inner">
          <div className="section-heading workflow-heading">
            <div>
              <div className="eyebrow"><span className="eyebrow-line" /> ALUR TINGKAT TINGGI</div>
              <h2>Dari check-in<br />hingga status perintah.</h2>
            </div>
            <p>APNs membangunkan perangkat. Perangkat kemudian terhubung ke server untuk mengambil perintah—payload perintah tidak dikirim melalui APNs.</p>
          </div>
          <div className="flow-list">
            {flow.map(([number, title, description], index) => (
              <div className="flow-step" key={number}>
                <div className="flow-number">{number}</div>
                <div className="flow-copy"><h3>{title}</h3><p>{description}</p></div>
                {index < flow.length - 1 && <div className="flow-connector" aria-hidden="true" />}
              </div>
            ))}
          </div>
          <a className="text-link" href={readmeUrl} target="_blank" rel="noreferrer">Baca dokumentasi protokol lengkap <ArrowIcon /></a>
        </div>
      </section>

      <section className="security-section shell" id="keamanan">
        <div className="security-icon"><ShieldIcon /></div>
        <div className="security-copy">
          <div className="eyebrow"><span className="eyebrow-line" /> KEAMANAN DIDAHULUKAN</div>
          <h2>Eksperimental. Transparan.<br />Bukan untuk deployment publik.</h2>
          <p>Validasi identitas perangkat, proses enrollment lengkap, dan pengujian menyeluruh masih perlu diselesaikan. Jangan daftarkan perangkat nyata atau membuka endpoint MDM ke internet sebelum kontrol tersebut diterapkan.</p>
          <div className="security-pills"><span><Mark>✓</Mark> Penggunaan berizin</span><span><Mark>✓</Mark> Batasan terdokumentasi</span><span><Mark>✓</Mark> Tanpa klaim bypass Activation Lock</span></div>
        </div>
        <a className="security-link" href={`${repositoryUrl}/blob/main/ABOUT.md`} target="_blank" rel="noreferrer">Baca catatan keamanan <ArrowIcon /></a>
      </section>

      <section className="closing-cta shell">
        <div className="closing-orb" />
        <div className="eyebrow"><span className="eyebrow-line" /> MULAI EKSPLORASI</div>
        <h2>Pelajari protokolnya.<br /><span>Bangun dengan bertanggung jawab.</span></h2>
        <p>Jelajahi kode sumber, jalankan pengujian lokal, dan bantu tingkatkan fondasi proyek.</p>
        <a className="button button-primary" href={repositoryUrl} target="_blank" rel="noreferrer">Buka repository di GitHub <ArrowIcon /></a>
      </section>

      <footer className="site-footer shell">
        <a className="brand footer-brand" href="#top"><span className="brand-icon"><ShieldIcon /></span><span>mdm<span className="brand-muted">.server</span></span></a>
        <p>Proyek pembelajaran open source · Pengelolaan perangkat yang sah dan berizin.</p>
        <div className="footer-links"><a href={readmeUrl}>Dokumentasi</a><a href={`${repositoryUrl}/blob/main/ABOUT.md`}>Tentang</a><a href={repositoryUrl} target="_blank" rel="noreferrer">GitHub ↗</a></div>
      </footer>
    </main>
  );
}
