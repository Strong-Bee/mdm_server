# MDM Server Web — Next.js + TypeScript

Antarmuka web untuk proyek Apple iOS/iPadOS MDM eksperimental.

## Fitur

- Landing page responsif berbahasa Indonesia.
- Dashboard inventaris perangkat di `/dashboard`.
- Kontrak tipe API bersama di `lib/mdm-types.ts`.
- Route Handlers Next.js untuk meneruskan permintaan ke API admin Flask.
- Antrean perintah dari daftar RequestType yang didukung backend.
- Token admin digunakan dalam sesi browser; backend token tidak disimpan ke kode sumber.

## Stack

- Next.js App Router
- React + TypeScript strict
- CSS responsif
- Next.js Route Handlers (Node.js runtime)

## Pengembangan lokal

Dari direktori ini:

```bash
npm install
cp .env.example .env.local
# Edit MDM_API_BASE_URL agar mengarah ke backend Flask.
npm run dev
```

Buka http://localhost:3000. Halaman utama berisi pengenalan proyek dan dashboard ada di http://localhost:3000/dashboard.

## Environment

`MDM_API_BASE_URL` adalah URL dasar backend Flask. Gunakan HTTPS untuk deployment selain localhost. Jangan menambahkan token admin ke variabel publik seperti `NEXT_PUBLIC_*`.

## Deployment Vercel

Import `Strong-Bee/mdm_server`, pilih preset **Next.js**, dan atur **Root Directory** menjadi `web`. Tambahkan `MDM_API_BASE_URL` di Project Settings → Environment Variables.

Deployment ini menerbitkan frontend Next.js dan proxy API dashboard saja. Backend MDM Flask/Python, SQLite, serta integrasi APNs tetap layanan terpisah. SQLite lokal pada serverless tidak cocok untuk penyimpanan produksi persisten. Jangan publikasikan endpoint MDM sebelum validasi identitas perangkat, enrollment, TLS, kontrol akses, dan pengujian keamanan selesai.

## Referensi

- [Backend repository](https://github.com/Strong-Bee/mdm_server)
- [README utama](https://github.com/Strong-Bee/mdm_server/blob/main/README.md)
- [Catatan keamanan proyek](https://github.com/Strong-Bee/mdm_server/blob/main/ABOUT.md)
