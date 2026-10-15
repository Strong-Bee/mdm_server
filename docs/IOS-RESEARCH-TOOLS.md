# Katalog Tool Riset iOS

Dokumen ini mencatat proyek open-source yang relevan dengan riset iOS/iPadOS, diagnostik perangkat, komunikasi layanan, jailbreak, dan analisis firmware. **Pencatatan bukan berarti tool telah dipasang, diintegrasikan, diuji, atau dijalankan oleh MDM Server.** Setiap tool tetap merupakan proyek terpisah dengan dependensi, lisensi, dukungan OS, dan risiko tersendiri.

## Batasan keamanan

Katalog ini bersifat referensi dan inventaris. Repository MDM tidak mengimplementasikan exploit bootrom, bypass Activation Lock, penghapusan status aktivasi, patch `mobileactivationd`, atau ramdisk yang dirancang untuk melewati kontrol kepemilikan. Gunakan perangkat yang Anda miliki atau yang pengelolaannya telah diotorisasi. Jangan mengunggah firmware, token, pairing records, activation records, atau kredensial perangkat ke layanan publik.

## Tool dan referensi

| Proyek | Area | Catatan integrasi |
|---|---|---|
| [libimobiledevice](https://github.com/libimobiledevice/libimobiledevice) | Komunikasi perangkat iOS | Referensi untuk layanan perangkat dan protokol pairing; build native dan dukungan OS perlu diverifikasi. |
| [go-ios](https://github.com/danielpaulus/go-ios) | Komunikasi iOS berbasis Go | Kandidat untuk diagnostik dan inventaris perangkat yang diotorisasi; bukan dependensi langsung Python/Next.js. |
| [pymobiledevice3](https://github.com/doronz88/pymobiledevice3) | Library Python untuk layanan iOS | Kandidat untuk eksperimen diagnostik Python; periksa versi Python dan dukungan iOS terkini. |
| [appium-ios-device](https://github.com/appium/appium-ios-device) | Utilitas komunikasi perangkat untuk ekosistem Appium | Library Node.js; sebagian alur bergantung pada layanan/platform Apple dan mungkin tidak lengkap di Windows. |
| [gaster](https://github.com/0x7ff/gaster) | Riset bootrom/checkm8 | Referensi riset tingkat rendah saja; tidak diintegrasikan atau dieksekusi oleh server web. |
| [ipwndfu](https://github.com/axi0mX/ipwndfu) | Riset bootrom/checkm8 | Referensi historis; kompatibilitas perangkat dan toolchain harus ditinjau terpisah. |
| [checkra1n](https://checkra.in/) | Riset jailbreak | Proyek eksternal; bukan komponen MDM. |
| [PongoOS](https://github.com/checkra1n/PongoOS) | Lingkungan pre-boot riset | Referensi arsitektur pre-boot; tidak dijalankan dari Vercel/browser. |
| [palera1n](https://github.com/palera1n/palera1n) | Riset jailbreak perangkat tertentu | Tool sistem eksternal, bukan dependensi web. |
| [jbinit](https://github.com/verygenericname/jbinit) | Riset boot/ramdisk | Referensi terpisah; tidak menjadi bagian runtime MDM. |
| [img4tool](https://github.com/tihmstar/img4tool) | Analisis kontainer firmware IMG4 | Kandidat untuk alur analisis firmware offline dengan input yang sah. |
| [iBoot64Patcher](https://github.com/tihmstar/iBoot64Patcher) | Riset bootloader | Referensi tingkat rendah; tidak dioperasionalkan oleh aplikasi web ini. |
| [ramdiskutil](https://github.com/verygenericname/ramdiskutil) | Analisis/customization ramdisk | Referensi terpisah; tidak diintegrasikan ke backend MDM. |
| [iExtractor](https://github.com) | Ekstraksi firmware IPSW | Nama proyek belum cukup spesifik untuk memastikan repository kanonis; verifikasi URL sumber sebelum penggunaan. |
| Lockra1n | Referensi yang disebut terkait activation bypass | Tidak diintegrasikan. URL dan provenance sumber harus diverifikasi terlebih dahulu. |
| LIBRE-HACKTIVATOR | Skrip per versi yang disebut terkait aktivasi | Tidak diintegrasikan. URL dan lisensi belum diverifikasi. |
| iOS-Hacktivation-Toolkit | Skrip patch aktivasi yang disebut per versi | Tidak diintegrasikan. URL dan lisensi belum diverifikasi. |
| Onii_Ramdisk | Tool ramdisk yang disebut terkait activation bypass | Tidak diintegrasikan. URL dan provenance sumber harus diverifikasi. |
| libideviceactivation | Aktivasi perangkat | Tinjau API dan lisensi upstream secara mandiri; tidak diintegrasikan untuk mengubah atau melewati status aktivasi. |

## Arsitektur integrasi yang disarankan

- **Web UI (Next.js):** tampilkan katalog, link upstream, status review, kompatibilitas, dan catatan lisensi.
- **Backend MDM (Python/Flask):** tetap menangani protokol MDM yang telah ada. Jangan menjalankan tool native atau perintah arbitrer dari request browser.
- **Worker diagnostik lokal (opsional):** jalankan hanya di host yang dikelola operator, dengan allowlist perintah, autentikasi, audit log, timeout, dan validasi input. Tidak tersedia di Vercel serverless.
- **CI:** lakukan lint/build/test aplikasi dan pemeriksaan metadata; jangan menjalankan exploit atau memproses perangkat fisik di CI publik.

## Sebelum memasang tool

1. Verifikasi URL upstream dan lisensi pada repository resmi.
2. Baca dokumentasi instalasi serta kebutuhan toolchain/OS.
3. Pin versi atau commit; hindari mengunduh skrip tidak terverifikasi saat runtime.
4. Uji dalam VM/lab dan perangkat yang diotorisasi.
5. Simpan secret dan data perangkat di luar Git; jangan mencatat token sensitif.
6. Catat hasil pengujian sebelum memberi status “supported”.

## Status saat ini

Semua entri di atas adalah **referensi katalog**, bukan klaim instalasi atau integrasi executable. Backend MDM dan frontend yang ada tetap dipertahankan.
