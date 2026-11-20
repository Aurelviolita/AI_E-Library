# AI e-Library v2.4 — Sampul Buku Resmi Google Books

## Yang berubah
- Sampul ilustrasi tidak lagi disamarkan sebagai cover asli.
- `GET /api/v1/catalog/{book_id}/cover` mengambil thumbnail dari Google Books **berdasarkan ID volume yang sudah ada pada source_url**, bukan pencarian gambar bebas.
- Thumbnail hanya digunakan bila judul cocok dengan katalog atau ISBN cocok dengan metadata volume. Host gambar dibatasi pada domain gambar Google yang diizinkan.
- Apabila metadata gagal, gambar tidak tersedia, atau identitas tidak cocok, frontend tetap memakai sampul ilustrasi yang diberi label **ILUSTRASI KATALOG**.
- Permintaan foto sampul dibuat saat elemen terlihat di layar (lazy), hasil metadata disimpan dalam cache proses backend.

## Cara menjalankan di Windows
1. Ekstrak ZIP ini, buka folder `E-book-Library--main` di VS Code.
2. Jalankan `setup_windows.bat` jika dependensi Python belum tersedia.
3. Terminal pertama: `./run_api.bat` (di PowerShell ` .\run_api.bat `).
4. Terminal kedua dari root proyek: `cd frontend`, lalu `npm.cmd ci` dan `npm.cmd run build`.
5. Buka `http://127.0.0.1:8000/`, tekan Ctrl+F5. Untuk mode dev gunakan `npm.cmd run dev` pada terminal kedua.
6. Cek `http://127.0.0.1:8000/api/v1/catalog/BK00001/cover` untuk melihat status verifikasi cover.

## Batasan
- Google Books API membutuhkan koneksi internet dan mempunyai pembatasan akses. Cover mungkin tidak tampil apabila metadata tidak tersedia atau tidak cocok.
- Cover tidak diunduh permanen untuk seluruh 973 judul, dan tidak dijanjikan bahwa semuanya punya sampul.
- Pengujian API dan logika verifikasi berjalan lokal menggunakan mock; **build React belum terverifikasi di lingkungan perbaikan** karena tidak tersedia seluruh cache paket NPM. Jalankan build di komputer Windows yang memiliki koneksi internet.
- Tidak ada perubahan pada bobot model BGE-M3 atau metrik evaluasi.
