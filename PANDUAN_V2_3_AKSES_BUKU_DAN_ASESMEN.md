# AI e-Library v2.3 — Akses Buku & Kejelasan Sumber Asesmen

## Perubahan
- Modal detail buku kini menampilkan **Lihat di Google Books** menggunakan `source_url` dari `data/dataset_buku_2000.csv`, dipasangkan ke katalog inferensi berdasarkan `book_id`.
- API baru `GET /api/v1/catalog/{book_id}/access` mengecek metadata publik Google Books saat detail buku dibuka. **Baca pratinjau** hanya ditampilkan bila API menyatakan `PARTIAL` atau `ALL_PAGES`. **Baca buku** penuh hanya bila API mengonfirmasi akses penuh. Jika gagal menghubungi Google Books, tautan halaman sumber tetap ditampilkan. Tidak ada PDF atau ebook berhak cipta yang disalin.
- Form *Competency Gap* kini menanyakan **sumber angka**: simulasi atau input manual dari asesmen resmi. Skala 0–5 diberi rubrik contoh. Ini **bukan skala resmi organisasi**. Nilai resmi seharusnya berasal dari proses asesmen HR/organisasi, sementara standar target berasal dari kamus/standar kompetensi jabatan yang disahkan.
- Tidak ada integrasi ke sistem asesmen karyawan internal. Server tidak menyimpan informasi asesmen pada endpoint ini; jangan memasukkan data identitas personal ketika demo.

## Jalankan dari folder `E-book-Library--main`
1. Jika baru ekstrak: jalankan `setup_windows.bat` (install Python/dependensi).
2. Backend di terminal pertama: `run_api.bat` atau `\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000`.
3. Frontend: buka terminal kedua lalu `cd frontend`, `npm.cmd ci`, `npm.cmd run build`.
4. Buka `http://127.0.0.1:8000/` dan refresh dengan Ctrl+F5. Alternatif development: `npm.cmd run dev`, lalu buka URL yang ditampilkan Vite.
5. Di katalog/rekomendasi, klik buku dan cari panel **Akses buku**. Untuk asesmen, buka **Rencana Belajar Sesuai Competency Gap** dan baca panduan sumber nilai.

## Tes
Dari folder proyek, setelah dependensi tersedia:
```
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_book_access_v23.py' -v
```

## Batasan
- Hak baca ditentukan oleh penerbit dan Google Books, bukan oleh aplikasi.
- Koneksi internet dibutuhkan untuk pemeriksaan status preview; API bisa rate-limit.
- Build React perlu dijalankan di Windows pengguna; lingkungan pembuat paket tidak memiliki seluruh dependensi NPM dalam cache, sehingga build frontend belum diverifikasi di sini.
- Skala nilai 0–5 semata ilustrasi. Untuk produksi, HR/penanggung jawab kompetensi harus mendefinisikan instrumen asesmen, rubrik per kompetensi, validasi nilai, standar jabatan, dan persetujuan pemrosesan data.
