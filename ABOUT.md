# Tentang Proyek

## Nama

**Apple iOS/iPadOS MDM Server & Security CVE Catalog**

## Ringkasan

Repositori sumber terbuka untuk mempelajari implementasi awal protokol Mobile Device Management (MDM) Apple, mengelola perangkat iOS/iPadOS yang terdaftar secara sah, dan mengumpulkan referensi CVE dari advisori keamanan resmi Apple. Proyek ini ditujukan untuk pembelajaran protokol, pengujian terkontrol, pengembangan, dan riset keamanan defensif.

## Tujuan proyek

- Mempelajari alur dasar komunikasi MDM Apple.
- Menyediakan endpoint check-in dan antrean perintah untuk perangkat yang sudah terdaftar.
- Menguji integrasi notifikasi push MDM melalui Apple Push Notification service (APNs).
- Menyediakan API administrasi yang memerlukan autentikasi.
- Menyinkronkan katalog CVE iOS/iPadOS dari advisori keamanan resmi Apple.
- Mendokumentasikan batasan, kebutuhan pengamanan, dan status pengujian secara terbuka.

## Fitur saat ini

- Endpoint dasar check-in dan perintah MDM berbasis plist.
- Penyimpanan metadata perangkat dan status perintah menggunakan SQLite.
- Integrasi APNs yang memerlukan kredensial resmi dan konfigurasi yang sesuai.
- Endpoint administrasi dengan token.
- Klien pendamping untuk melihat perangkat dan mengantrekan perintah `DeviceInformation`.
- Skrip Python untuk mengumpulkan ID CVE dari advisori keamanan Apple.
- Workflow GitHub Actions untuk sinkronisasi katalog CVE terjadwal/manual.
- Pengujian unit dasar dan CI.

## Teknologi

- Python
- Flask
- SQLite
- Apple Mobile Device Management (MDM) protocol
- Apple Push Notification service (APNs)
- JSON, XML property lists (plist)
- GitHub Actions

## Status pengembangan

**Eksperimental — belum siap untuk produksi.**

Implementasi ini belum mencakup seluruh persyaratan protokol dan keamanan untuk layanan MDM komersial. Sebelum penggunaan nyata, proyek memerlukan validasi identitas perangkat, alur enrollment dan profil yang lengkap, konfigurasi TLS yang benar, pemeriksaan otorisasi, pencatatan audit, penanganan rahasia, serta pengujian menyeluruh pada perangkat iPhone/iPad yang berwenang.

Katalog CVE menghimpun ID yang ditemukan pada advisori Apple. Katalog tersebut tidak menjamin cakupan seluruh CVE dari setiap basis data pihak ketiga, laporan yang belum dipublikasikan, atau kerentanan yang belum diberi ID CVE. Detail versi terdampak dan tingkat keparahan hanya boleh dianggap terverifikasi jika dinyatakan oleh sumber yang sesuai.

## Penggunaan yang diizinkan

Gunakan proyek hanya pada perangkat milik sendiri atau perangkat yang pengelolaannya telah diizinkan secara eksplisit. Lindungi token administrator, kredensial APNs, token perangkat, dan basis data. Jangan mengekspos server ke internet publik sebelum kontrol keamanan yang diperlukan selesai dan diverifikasi.

Proyek ini **tidak menyediakan fitur bypass Activation Lock** dan tidak dimaksudkan untuk melewati autentikasi, kepemilikan, atau kontrol keamanan Apple.

## Sumber resmi

- [Apple Device Management](https://developer.apple.com/documentation/devicemanagement/)
- [Dokumentasi payload MDM](https://developer.apple.com/documentation/devicemanagement/mdm)
- [Rilis Keamanan Apple](https://support.apple.com/en-us/100100)
- [Apple Software Lookup Service](https://gdmf.apple.com/v2/pmv)

## Kontribusi

Kontribusi dapat berupa perbaikan bug, pengujian protokol, peningkatan dokumentasi, penguatan keamanan, atau peningkatan kualitas sinkronisasi CVE. Sertakan langkah reproduksi, hasil pengujian, referensi resmi, dan dampak keamanan pada setiap perubahan yang relevan.

Jangan menyertakan kredensial, token, data pribadi perangkat, atau detail eksploitasi yang dapat membahayakan pengguna dalam issue maupun pull request.

## Lisensi

Periksa berkas lisensi pada repositori sebelum menggunakan, memodifikasi, atau mendistribusikan proyek ini. Jika repositori belum menyertakan berkas lisensi, hak penggunaan ulang oleh pihak lain belum diberikan secara otomatis.
