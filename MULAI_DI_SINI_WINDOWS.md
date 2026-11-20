# Menjalankan AI e-Library di Windows (versi debug v2.2)

**Penting:** Jangan jalankan perintah pada folder ZIP terluar. Masuk ke folder yang mengandung `api.py`, `frontend`, `models`, dan `tests`.

## Sekali saja
1. Ekstrak ZIP lalu buka folder proyek di VS Code.
2. Periksa versi Python dengan `py -0p` dan Node dengan `node --version`.
3. Jalankan `setup_windows.bat` atau `py -3.12 -m venv .venv` (jika Python 3.12 tersedia), kemudian `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
4. Jalankan preflight: `.\.venv\Scripts\python.exe scripts\preflight.py`.

## Setiap menjalankan
- Terminal 1: jalankan `run_api.bat`; API dokumentasi: http://127.0.0.1:8000/docs
- Terminal 2: jalankan `run_frontend.bat`; gunakan URL localhost yang dicetak oleh Vite (biasanya 5173).

## Mengapa ada fallback?
- Model utama BGE-M3 memiliki **embedding katalog/kompetensi yang sudah dihitung**, jadi pencarian buku berdasarkan kompetensi berjalan tanpa harus menjalankan notebook atau download transformer.
- Bobot BGE-M3 neural untuk **meng-encode judul/abstrak buku baru** tidak ada dalam ZIP. Mode fallback TF-IDF digunakan secara eksplisit dengan penanda `is_fallback=true` saat bobot neural tak tersedia. Untuk memakai model neural asli, install `requirements-semantic.txt` dan sediakan/cache bobot `BAAI/bge-m3`; menjalankan dengan `ELIBRARY_DOWNLOAD_MODEL=1` mengizinkan download via Hugging Face (perlu internet dan resource cukup).
- Model tidak perlu dilatih ulang setiap kali BE/FE dibuka.

## Tes
- `.\.venv\Scripts\python.exe -m pytest tests/test_personalized_learning.py tests/test_integration.py tests/test_new_book.py -q`
- Test dashboard lengkap memerlukan `cd frontend && npm.cmd install && npm.cmd run build` lebih dulu.

Jika `venvlauncher.exe` gagal disalin, tutup VS Code/terminal yang memakai `.venv`, hapus folder `.venv` yang rusak, lalu buat ulang.

## Batasan hasil debugging
- Pipeline TF-IDF untuk buku baru bisa mengembalikan **daftar kosong** apabila judul/abstrak tidak memiliki kecocokan dengan kosakata model. Ini tidak dianggap sebagai kegagalan server; kualitas relevansinya perlu dievaluasi dan dikalibrasi dengan benchmark baru.
- `GET /health` menunjukkan server dan artefak yang siap digunakan, **bukan** jaminan bahwa bobot transformer neural sudah terunduh. Pada instalasi tanpa bobot, respons pemetaan buku baru harus menunjukkan fallback.
- Build React belum diverifikasi di lingkungan debugging karena pemasangan paket NPM tidak selesai; uji manual melalui `run_frontend.bat` di Windows masih diperlukan.
