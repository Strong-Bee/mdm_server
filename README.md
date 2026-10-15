# Server MDM Apple iOS/iPadOS

Implementasi dasar protokol **Mobile Device Management (MDM)** Apple menggunakan Python dan Flask untuk eksperimen serta administrasi iPhone dan iPad yang **sah dan telah mendapat izin**.

> **Status: eksperimental — belum siap untuk produksi.** Repositori ini belum merupakan produk MDM Apple yang lengkap. Jangan membuka server ke internet publik atau mendaftarkan perangkat nyata sebelum kepercayaan proses enrollment, TLS, otorisasi, validasi perintah, dan pengujian menyeluruh diselesaikan.

## Ruang lingkup

Proyek ini ditujukan untuk perangkat Apple iOS/iPadOS dan mencakup implementasi awal berikut:

- Menangani pesan check-in Apple berbasis plist: `Authenticate`, `TokenUpdate`, dan `CheckOut`.
- Endpoint koneksi perintah MDM yang mengembalikan perintah dalam antrean sebagai respons plist.
- Penyimpanan SQLite untuk pengenal perangkat, metadata enrollment/push, informasi inventaris dasar, dan status perintah.
- Dukungan notifikasi push MDM melalui APNs menggunakan kredensial yang diberikan melalui variabel lingkungan.
- Endpoint API administrasi yang dilindungi token.
- Pengujian unit Python dasar dan CI melalui GitHub Actions.

### Batasan penting

Proyek ini merupakan dasar implementasi protokol, bukan server MDM lengkap yang siap produksi. Hal-hal berikut masih perlu diselesaikan:

- Pembuatan, penandatanganan, dan verifikasi profil enrollment belum tersedia sebagai alur enrollment yang lengkap.
- Validasi identitas perangkat dan sertifikat klien MDM harus diterapkan serta diverifikasi pada lapisan TLS/proxy terbalik sebelum server boleh diakses publik.
- Payload dan respons perintah Apple memerlukan validasi skema yang lengkap serta cakupan protokol yang lebih luas.
- Perilaku APNs perlu diuji dengan kredensial resmi Apple yang valid dan perangkat yang telah terdaftar.
- Pengujian saat ini masih berupa pengujian dasar; pengujian tersebut tidak menggantikan pengujian menyeluruh pada iPhone/iPad nyata.
- Fitur bypass Activation Lock **tidak tersedia** dan tidak dijanjikan oleh proyek ini.

## Arsitektur

Komunikasi MDM Apple umumnya memiliki dua jalur berbeda:

1. **Layanan check-in** — perangkat mengirim pesan enrollment/check-in ke endpoint `/checkin`.
2. **Layanan perintah MDM** — APNs membangunkan perangkat; perangkat kemudian terhubung ke endpoint `/mdm` untuk mengambil perintah yang mengantre dan melaporkan hasilnya.

APNs hanya berfungsi sebagai sinyal untuk membangunkan perangkat, bukan sebagai saluran yang membawa isi perintah. Perangkat terhubung ke server MDM untuk mengambil perintah.

## Persyaratan

- Python 3.11 atau lebih baru (CI saat ini menggunakan Python 3.11).
- Dependensi yang tercantum dalam `requirements.txt`.
- Direktori permanen yang dapat ditulisi untuk basis data SQLite.
- Untuk notifikasi push ke perangkat nyata: konfigurasi dan kredensial APNs/MDM Apple yang valid.
- HTTPS dengan sertifikat yang valid untuk setiap deployment yang melayani perangkat.

## Menjalankan secara lokal

### 1. Kloning repositori dan instal dependensi

```bash
git clone https://github.com/Strong-Bee/mdm_server.git
cd mdm_server
python -m venv .venv
```

Aktifkan lingkungan virtual:

**Linux/macOS**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.venv\\Scripts\\Activate.ps1
```

Instal dependensi:

```bash
python -m pip install -r requirements.txt
```

### 2. Atur variabel lingkungan

Buat secret dan token administrator yang kuat serta unik. Jangan pernah memasukkan secret asli ke Git.

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
$env:MDM_DATABASE_PATH = "$PWD\\mdm.db"
$env:MDM_HOST = "127.0.0.1"
$env:PORT = "8000"
```

Untuk APNs, atur variabel yang dibutuhkan oleh `apns_push.py`:

- `APNS_TEAM_ID`
- `APNS_KEY_ID`
- `APNS_AUTH_KEY_PATH` — lokasi berkas kunci autentikasi APNs yang diterbitkan Apple.
- `APNS_USE_SANDBOX` — gunakan `true` hanya jika lingkungan dan token dikonfigurasi untuk APNs sandbox; selain itu gunakan `false`.

Simpan kunci APNs di luar repositori dan batasi izin akses berkasnya. Kredensial APNs dan token perangkat harus diperlakukan sebagai informasi rahasia.

### 3. Jalankan server

```bash
python main.py
```

Alamat bind bawaan adalah `127.0.0.1:8000`. Secara sengaja, server hanya menerima koneksi lokal secara bawaan. Jangan mengikat server ke antarmuka publik sebelum TLS, pemeriksaan identitas perangkat, dan kontrol deployment dikonfigurasi.

Pengaturan TLS opsional untuk penggunaan lokal/pengujian:

- `SSL_CERT_FILE`
- `SSL_KEY_FILE`

Keduanya harus menunjuk ke berkas yang tersedia agar konteks TLS bawaan diaktifkan. Untuk produksi, gunakan proxy terbalik HTTPS yang dikonfigurasi dengan benar dan implementasikan validasi identitas klien MDM Apple yang diperlukan.

### 4. Periksa status layanan

```bash
curl http://127.0.0.1:8000/health
```

Respons yang diharapkan:

```json
{
  "status": "ok",
  "service": "apple-ios-mdm"
}
```

Endpoint kesehatan hanya memastikan aplikasi Flask merespons; endpoint ini tidak memverifikasi enrollment Apple atau konektivitas APNs.

## Endpoint yang tersedia

| Metode | Endpoint | Fungsi |
|---|---|---|
| GET | `/health` | Pemeriksaan kesehatan layanan dasar |
| POST / PUT | `/checkin` | Menerima pesan check-in plist Apple MDM yang didukung |
| PUT | `/mdm` | Menerima permintaan/respons MDM perangkat dan mengembalikan perintah tertunda jika tersedia |
| POST | `/api/admin/login` | Memulai sesi administrator menggunakan `MDM_ADMIN_TOKEN` |
| POST | `/api/admin/logout` | Mengakhiri sesi administrator |
| GET | `/api/devices` | Menampilkan inventaris perangkat; memerlukan autentikasi administrator |
| POST | `/api/devices/<udid>/commands` | Memasukkan perintah MDM yang diizinkan ke antrean; memerlukan autentikasi administrator |

Endpoint check-in dan MDM mengharapkan isi permintaan plist Apple, bukan JSON sembarang. Endpoint yang diakses perangkat belum aman untuk dibuka ke publik sebelum enrollment dan validasi identitas perangkat tersedia.

### Contoh penggunaan API administrasi

Menampilkan daftar perangkat menggunakan token bearer:

```bash
curl -H "Authorization: Bearer $MDM_ADMIN_TOKEN" \\
  http://127.0.0.1:8000/api/devices
```

Memasukkan permintaan informasi dasar perangkat yang sudah terdaftar ke antrean:

```bash
curl -X POST \\
  -H "Authorization: Bearer $MDM_ADMIN_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"command_type":"DeviceInformation","payload":{}}' \\
  "http://127.0.0.1:8000/api/devices/<UDID>/commands"
```

Ganti `<UDID>` dengan UDID perangkat yang sudah terdaftar. API melaporkan apakah notifikasi APNs telah dikirim; perintah yang berhasil masuk antrean atau notifikasi yang berhasil dikirim **tidak menjamin** perangkat telah menjalankan perintah tersebut. Periksa respons/status perintah dan log perangkat.

Gunakan perintah hanya pada perangkat milik Anda atau perangkat yang secara eksplisit Anda berwenang untuk kelola. Perintah seperti `EraseDevice` bersifat merusak data dan harus dilindungi dengan konfirmasi tambahan serta pencatatan audit sebelum penggunaan produksi.

## Basis data

Basis data SQLite bawaan adalah `mdm.db` di direktori proyek. Atur `MDM_DATABASE_PATH` untuk menggunakan lokasi lain. Cadangkan basis data sebelum menguji perubahan skema atau menjalankan migrasi. Skema saat ini menyimpan metadata perangkat dan push yang bersifat sensitif; lindungi berkas basis data beserta cadangannya.

## Pengujian

Setelah dependensi terpasang, jalankan:

```bash
python -m compileall -q app main.py apns_push.py tests integrations
python -m unittest discover -s tests -v
```

GitHub Actions menjalankan kompilasi Python dan pengujian unit saat ada push ke branch `main` dan `fix/**`, serta saat ada pull request yang menargetkan `main`. Periksa hasil CI terbaru sebelum menggabungkan perubahan.

## Daftar pemeriksaan kesiapan produksi

- [ ] Selesaikan alur profil enrollment yang ditandatangani dan verifikasi pemasangan profil/enrollment.
- [ ] Wajibkan HTTPS dan validasi identitas perangkat/sertifikat klien sesuai persyaratan MDM Apple.
- [ ] Lindungi endpoint enrollment/check-in dari pemalsuan identitas dan permintaan tanpa izin.
- [ ] Validasi setiap perintah dan respons yang didukung berdasarkan skema protokol Apple.
- [ ] Verifikasi topik APNs, PushMagic, token perangkat, dan kredensial menggunakan perangkat uji nyata yang sudah terdaftar.
- [ ] Tambahkan log audit, pembatasan laju permintaan, pemantauan, pencadangan, dan kontrol retensi data.
- [ ] Tambahkan pengujian menyeluruh untuk enrollment, TokenUpdate, pengiriman perintah, hasil perintah, dan CheckOut.
- [ ] Tinjau izin untuk perintah yang merusak data dan wajibkan konfirmasi eksplisit.
- [ ] Rotasi semua secret dan batasi akses ke basis data serta kunci APNs.

## Referensi

- [Dokumentasi Apple Device Management](https://developer.apple.com/documentation/devicemanagement)
- [Apple MDM Check-in](https://developer.apple.com/documentation/devicemanagement/check-in)
- [Mengirim perintah MDM ke perangkat](https://developer.apple.com/documentation/devicemanagement/sending-mdm-commands-to-a-device)

## Lisensi

Periksa berkas lisensi di repositori sebelum mendistribusikan ulang atau menggunakan proyek ini dalam produk komersial.
