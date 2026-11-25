"""REST API Produksi: BPJS Kesehatan AI e-Library Recommender Service.

Layanan backend siap deploy (FastAPI) untuk integrasi langsung ke portal
AI e-Library dan Human Capital Management (HCM) BPJS Kesehatan.

Fitur Utama:
1. Pemetaan Buku Baru ke Multikompetensi (Katalogisasi Otomatis e-Library)
2. Rekomendasi Buku Katalog untuk Menutup Competency Gap Karyawan
3. Penjelajahan Kamus 67 Kompetensi Kerja BPJS Kesehatan
4. Pencarian Koleksi 973 Buku Katalog e-Library
5. Dokumentasi Interaktif Swagger UI (/docs) & ReDoc (/redoc)
6. Dasbor Pengujian Web Interaktif di Root (/)
"""
from __future__ import annotations
import os
import sys
import time
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import urlparse, parse_qs, quote
from urllib.request import urlopen, Request
import json
from functools import lru_cache

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Pastikan workspace root ada di path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.recommender import BookRecommender
from src.simulation import SIMULATION_PROFILES, run_simulation_recommendation

# Inisialisasi Model Produksi
MODEL_DIR = ROOT / "models" / "best_model"
FALLBACK_MODEL_DIR = ROOT / "models" / "candidates" / "tfidf"
DASHBOARD_DIR = ROOT / "frontend" / "dist"

# Katalog embedding sengaja ringkas; metadata tautan disimpan dalam dataset asal.
@lru_cache(maxsize=1)
def book_source_index() -> dict[str, str]:
    source_file = ROOT / "data" / "dataset_buku_2000.csv"
    if not source_file.exists():
        return {}
    df = pd.read_csv(source_file, usecols=["book_id", "source_url"], dtype=str).fillna("")
    return {str(row.book_id): url for row in df.itertuples(index=False)
            if (url := safe_google_books_url(row.source_url))}

try:
    # Muat model terbaik (BGE-M3 dengan transparansi fallback jika resource terbatas)
    recommender = BookRecommender.load(MODEL_DIR, allow_fallback=True,
                                      local_files_only=os.environ.get('ELIBRARY_DOWNLOAD_MODEL', '0') != '1')
    print(f"[*] AI e-Library Engine Loaded: {recommender.model_name} (Aktual: {recommender.actual_model_name})")
except Exception as e:
    print(f"[!] Warning: Gagal memuat best_model ({e}), beralih ke TF-IDF candidate...")
    recommender = BookRecommender.load(FALLBACK_MODEL_DIR)

app = FastAPI(
    title="BPJS Kesehatan AI e-Library Recommendation API",
    description=(
        "API Resmi Layanan Rekomendasi Buku & Pemetaan Kompetensi Kerja Karyawan BPJS Kesehatan. "
        "Dirancang untuk integrasi sistem Human Capital Management (HCM), Corporate University, "
        "dan portal perpustakaan digital (AI e-Library) BPJS Kesehatan."
    ),
    version="2.4.0",
    contact={
        "name": "Tim NLP & AI Kediklatan BPJS Kesehatan",
        "email": "learning@bpjs-kesehatan.go.id"
    }
)

# Aktifkan CORS agar frontend (React, Vue, Flutter, Next.js) dapat langsung memanggil API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(
    "/dashboard-assets",
    StaticFiles(directory=DASHBOARD_DIR / "dashboard-assets", check_dir=False),
    name="dashboard-assets",
)


# =============================================================================
# PYDANTIC SCHEMAS (REQUEST & RESPONSE MODELS)
# =============================================================================

class CompetencyItem(BaseModel):
    rank: int = Field(..., description="Urutan peringkat relevansi (1 = teratas)")
    competency_id: str = Field(..., description="Kode unik kompetensi BPJS (e.g. C023)")
    competency_name: str = Field(..., description="Nama resmi kompetensi kerja")
    score: float = Field(..., description="Skor kecocokan semantik (0.0 - 1.0)")
    confidence: str = Field(..., description="Tingkat keyakinan: SANGAT_TINGGI, TINGGI, SEDANG, INDIKATIF")
    model: str = Field(..., description="Nama model inferensi yang mengeksekusi")
    model_type: str = Field(..., description="Tipe arsitektur model (dense_biencoder / lexical)")
    is_fallback: bool = Field(..., description="Apakah inferensi menggunakan mode fallback")
    latency_breakdown_ms: dict[str, float] = Field(..., description="Rincian waktu inferensi per tahap (ms)")


class BookToCompetenciesRequest(BaseModel):
    title: str = Field(..., min_length=2, example="Healthcare Risk Mitigation Handbook", description="Judul buku (Bahasa Indonesia atau Inggris)")
    abstract: str = Field(..., min_length=5, example="This handbook discusses operational risk identification, clinical safety assessment, and compliance in hospital facilities.", description="Abstrak atau sinopsis buku")
    top_k: int = Field(5, ge=1, le=10, description="Jumlah maksimal rekomendasi kompetensi")
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Ambang batas skor minimum (opsional, default adaptif)")


class BookToCompetenciesResponse(BaseModel):
    status: str = "success"
    query_title: str
    total_recommendations: int
    execution_time_ms: float
    recommendations: list[CompetencyItem]


class BookItem(BaseModel):
    rank: int
    book_id: str
    judul: str
    author: str
    tahun: str
    kategori: str
    score: float
    skor_model: float
    model: str
    is_fallback: bool
    query_latency_ms: float


class CompetencyToBooksRequest(BaseModel):
    competency_id: str = Field(..., example="C023", description="ID Kompetensi BPJS (e.g. C023 untuk Risk Management)")
    top_k: int = Field(5, ge=1, le=20, description="Jumlah rekomendasi buku yang diinginkan")
    categories: list[str] | None = Field(None, description="Nama kategori katalog yang disertakan sebelum menentukan peringkat")


class CompetencyToBooksResponse(BaseModel):
    status: str = "success"
    competency_id: str
    competency_name: str
    total_books: int
    query_time_ms: float
    books: list[BookItem]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    active_model: str
    model_type: str
    is_fallback: bool
    catalog_books_count: int
    competencies_count: int
    uptime_seconds: float
    embedding_dimension: int | None = None
    new_book_model_ready: bool = False
    catalog_embeddings_ready: bool = False
    catalog_exported_at: str | None = None


START_TIME = time.time()


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
def home_dashboard():
    """Dasbor visual interaktif Pusat Wawasan Pembelajaran AI e-Library BPJS Kesehatan."""
    index = DASHBOARD_DIR / "index.html"
    if not index.is_file():
        return HTMLResponse(
            "<h1>Dasbor belum dibangun</h1><p>Jalankan npm ci dan npm run build di folder frontend.</p>",
            status_code=503,
        )
    return FileResponse(index, media_type="text/html")


@app.get("/health", response_model=HealthResponse, tags=["Sistem"])
def health_check():
    """Pengecekan status kesehatan layanan backend dan model inferensi aktif."""
    model_type_str = (
        "dense_biencoder" if (recommender.model_name in ("bge_m3", "e5") and not recommender.is_fallback_active)
        else "lexical_tfidf_fallback" if recommender.is_fallback_active
        else "lexical_tfidf" if recommender.model_name == "tfidf"
        else "lexical_bm25"
    )
    # Precomputed katalog tersedia untuk pencarian, tetapi belum tentu tersedia
    # bobot neural untuk encoding judul/abstrak buku yang baru.
    from importlib.util import find_spec
    weights_present = any((ROOT / 'local_models' / 'bge-m3').glob('*.safetensors')) if (ROOT / 'local_models' / 'bge-m3').exists() else False
    encoder_ready = recommender._encoder is not None or (find_spec('sentence_transformers') is not None and weights_present)
    catalog_ready = (MODEL_DIR / 'catalog_vectors.npy').exists()
    return {
        "status": "healthy",
        "new_book_model_ready": bool(encoder_ready or recommender._fallback_vectorizer is not None),
        "catalog_embeddings_ready": bool(catalog_ready),
        "service": "BPJS Kesehatan AI e-Library Recommendation API",
        "version": "2.3.0",
        "active_model": recommender.actual_model_name,
        "model_type": model_type_str,
        "is_fallback": recommender.is_fallback_active,
        "catalog_books_count": len(recommender.catalog) if recommender.catalog is not None else 0,
        "competencies_count": len(recommender.profiles),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "embedding_dimension": recommender.manifest.get("embedding_dimension") if model_type_str == "dense_biencoder" else None,
        "catalog_exported_at": recommender.manifest.get("export_timestamp"),
    }


@app.post("/api/v1/recommend-competencies", response_model=BookToCompetenciesResponse, tags=["Rekomendasi e-Library"])
def map_book_to_competencies(req: BookToCompetenciesRequest):
    """
    Fungsi 1: Pemetaan Buku Baru ke Multikompetensi (Katalogisasi Otomatis AI e-Library).
    
    Menerima judul dan abstrak buku baru (Bahasa Indonesia atau Inggris), lalu
    menghasilkan 1 hingga 5 kompetensi kerja BPJS Kesehatan yang paling relevan
    menggunakan kalibrasi ambang dinamis (Dynamic Score Margin).
    """
    t0 = time.perf_counter()
    try:
        results = recommender.map_book(
            title=req.title,
            abstract=req.abstract,
            top_k=req.top_k,
            min_score=req.min_score
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return {
        "status": "success",
        "query_title": req.title,
        "total_recommendations": len(results),
        "execution_time_ms": round(elapsed_ms, 2),
        "recommendations": results
    }


@app.post("/api/v1/recommend-books", response_model=CompetencyToBooksResponse, tags=["Rekomendasi e-Library"])
def recommend_books_for_competency(req: CompetencyToBooksRequest):
    """
    Fungsi 2: Rekomendasi Buku Katalog untuk Menutup Competency Gap Pegawai.
    
    Menerima ID Kompetensi BPJS (misal C023 - Risk Management), lalu mengambil
    daftar buku katalog terbaik yang paling sesuai untuk dipelajari pegawai.
    Beroperasi secara super cepat (~3.8 ms) menggunakan matriks vektor terkomputasi.
    """
    t0 = time.perf_counter()
    try:
        books = recommender.recommend_books_for_competency(
            competency_id=req.competency_id,
            top_k=req.top_k,
            categories=req.categories,
        )
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Cari nama kompetensi
    comp_row = recommender.profiles[recommender.profiles["competency_id"] == req.competency_id]
    comp_name = comp_row.iloc[0]["competency_name"] if len(comp_row) > 0 else req.competency_id

    return {
        "status": "success",
        "competency_id": req.competency_id,
        "competency_name": comp_name,
        "total_books": len(books),
        "query_time_ms": round(elapsed_ms, 2),
        "books": books
    }


@app.get("/api/v1/competencies", tags=["Data Referensi"])
def list_competencies():
    """Mengambil daftar lengkap 67 profil kompetensi kerja BPJS Kesehatan."""
    comps = recommender.profiles[["competency_id", "competency_name"]].to_dict(orient="records")
    return {
        "status": "success",
        "total": len(comps),
        "competencies": comps
    }


@app.get("/api/v1/catalog", tags=["Data Referensi"])
def list_catalog_books(
    q: Optional[str] = Query(None, description="Kata kunci pencarian judul atau penulis"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[list[str]] = Query(None, description="Kategori buku yang dicari"),
    sort: Optional[Literal["newest", "oldest", "title"]] = Query(None, description="Urutan tahun terbit atau judul"),
):
    """Mencari atau menampilkan daftar koleksi katalog buku e-Library internal BPJS."""
    if recommender.catalog is None:
        raise HTTPException(status_code=503, detail="Katalog buku belum dimuat")

    df = recommender.catalog
    if q:
        q_lower = q.lower()
        matching_titles = df["judul"].str.lower().str.contains(q_lower, regex=False, na=False)
        matching_authors = df["author"].str.lower().str.contains(q_lower, regex=False, na=False)
        df = df[matching_titles | matching_authors]
    if category:
        df = df[df["kategori_buku"].isin(category)]
    if sort in ("newest", "oldest"):
        df = df.sort_values("tahun", ascending=sort == "oldest", key=lambda years: pd.to_numeric(years, errors="coerce"), kind="stable")
    elif sort == "title":
        df = df.sort_values("judul", key=lambda titles: titles.str.strip().str.casefold(), kind="stable")

    total_matched = len(df)
    subset = df.iloc[offset:offset+limit]
    cols = [c for c in ["book_id", "judul", "author", "tahun", "kategori_buku"] if c in subset.columns]
    books = subset[cols].to_dict(orient="records")

    return {
        "status": "success",
        "total_matched": total_matched,
        "limit": limit,
        "offset": offset,
        "books": books
    }


class CatalogBookDetail(BaseModel):
    book_id: str
    abstrak: str
    source_url: str | None = None


def safe_google_books_url(raw: object) -> str | None:
    """Hanya izinkan tautan HTTPS/HTTP dari host Google Books resmi."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    parsed = urlparse(raw.strip())
    allowed = {"books.google.co.id", "books.google.com", "play.google.com"}
    if parsed.scheme not in ("https", "http") or parsed.hostname not in allowed:
        return None
    return parsed._replace(scheme="https").geturl()


def google_books_volume_id(source_url: str | None) -> str | None:
    if not source_url:
        return None
    parsed = urlparse(source_url)
    volume_id = parse_qs(parsed.query).get("id", [None])[0]
    if volume_id and len(volume_id) <= 80 and all(c.isalnum() or c in "_-" for c in volume_id):
        return volume_id
    return None


@lru_cache(maxsize=1)
def book_identity_index() -> dict[str, dict[str, str]]:
    """Identitas buku dari katalog sumber untuk verifikasi cover asli."""
    source_file = ROOT / "data" / "dataset_buku_2000.csv"
    if not source_file.exists():
        return {}
    df = pd.read_csv(source_file, usecols=["book_id", "judul", "author", "isbn"], dtype=str).fillna("")
    return {str(row.book_id): {"title": str(row.judul), "author": str(row.author),
                               "isbn": str(row.isbn)} for row in df.itertuples(index=False)}


@lru_cache(maxsize=1024)
def google_books_volume(volume_id: str) -> dict:
    """Lookup Google Books berdasarkan volume ID asli; tidak mencari gambar berdasarkan kata kunci."""
    endpoint = f"https://www.googleapis.com/books/v1/volumes/{quote(volume_id, safe='')}"
    request = Request(endpoint, headers={"User-Agent": "AI-eLibrary-Prototype/2.4"})
    with urlopen(request, timeout=4) as response:
        return json.load(response)


def normalized_title(value: str) -> str:
    import re
    import unicodedata
    value = unicodedata.normalize("NFKD", value).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", value))


def verified_cover_url(payload: dict, identity: dict[str, str]) -> tuple[str | None, str]:
    """Tolak thumbnail ketika identitas volume tidak cocok dengan katalog."""
    from difflib import SequenceMatcher
    volume = payload.get("volumeInfo") or {}
    expected_title = normalized_title(identity.get("title", ""))
    actual_title = normalized_title(str(volume.get("title") or ""))
    isbn = "".join(c for c in identity.get("isbn", "") if c.isdigit() or c.upper() == "X")
    isbn_match = bool(isbn and isbn in {
        "".join(c for c in str(item.get("identifier", "")) if c.isdigit() or c.upper() == "X")
        for item in volume.get("industryIdentifiers", []) if item.get("type") in ("ISBN_10", "ISBN_13")
    })
    title_match = bool(expected_title and actual_title and
                       (expected_title == actual_title or
                        SequenceMatcher(None, expected_title, actual_title).ratio() >= 0.88))
    if not (isbn_match or title_match):
        return None, "identity_mismatch"
    images = volume.get("imageLinks") or {}
    raw = images.get("thumbnail") or images.get("smallThumbnail")
    if not isinstance(raw, str):
        return None, "no_official_thumbnail"
    url = urlparse(raw)
    hostname = (url.hostname or "").lower()
    allowed = (hostname in ("books.google.com", "books.google.co.id", "books.googleusercontent.com")
               or hostname.endswith(".googleusercontent.com") or hostname.endswith(".ggpht.com"))
    if url.scheme not in ("http", "https") or not allowed:
        return None, "unsafe_thumbnail_url"
    return url._replace(scheme="https").geturl(), "verified_google_books"


@app.get("/api/v1/catalog/{book_id}/cover", tags=["Data Referensi"])
def get_catalog_cover(book_id: str):
    """Hanya cover Google Books yang terverifikasi identitasnya, selain itu placeholder UI."""
    identity = book_identity_index().get(book_id)
    if identity is None:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")
    volume_id = google_books_volume_id(book_source_index().get(book_id))
    if not volume_id:
        return {"book_id": book_id, "cover_url": None, "status": "source_unavailable"}
    try:
        cover_url, status_code = verified_cover_url(google_books_volume(volume_id), identity)
        return {"book_id": book_id, "cover_url": cover_url, "status": status_code}
    except Exception:
        return {"book_id": book_id, "cover_url": None, "status": "metadata_unavailable"}


@lru_cache(maxsize=1024)
def google_books_access(volume_id: str) -> dict:
    """Metadata akses Google Books, diminta saat pengguna membuka detail buku.

    Tidak perlu API key untuk lookup publik; bila jaringan/rate limit gagal,
    caller tetap memperoleh source_url yang tersimpan pada katalog.
    """
    payload = google_books_volume(volume_id)
    access = payload.get("accessInfo") or {}
    volume = payload.get("volumeInfo") or {}
    viewability = access.get("viewability", "UNKNOWN")
    return {
        "viewability": viewability,
        "is_full_readable": bool(access.get("accessViewStatus") == "FULL_PUBLIC_DOMAIN" or viewability == "ALL_PAGES"),
        "preview_url": safe_google_books_url(volume.get("previewLink")) if viewability in ("PARTIAL", "ALL_PAGES") else None,
        "web_reader_url": safe_google_books_url(access.get("webReaderLink")) if viewability in ("PARTIAL", "ALL_PAGES") else None,
    }


@app.get("/api/v1/catalog/{book_id}", response_model=CatalogBookDetail, tags=["Data Referensi"])
def get_catalog_book(book_id: str):
    """Mengambil ringkasan buku dari data katalog."""
    catalog = recommender.catalog
    if catalog is None:
        raise HTTPException(status_code=503, detail="Katalog buku belum dimuat")

    matches = catalog.loc[catalog["book_id"] == book_id]
    if matches.empty:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")

    row = matches.iloc[0]
    return {"book_id": book_id, "abstrak": str(row.get("abstrak", "")),
            "source_url": book_source_index().get(str(book_id))}


@app.get("/api/v1/catalog/{book_id}/access", tags=["Akses Buku"])
def get_book_access(book_id: str):
    """Cek ketersediaan preview secara on-demand; tidak menyediakan file buku penuh."""
    catalog = recommender.catalog
    if catalog is None:
        raise HTTPException(status_code=503, detail="Katalog belum dimuat")
    matches = catalog.loc[catalog["book_id"] == book_id]
    if matches.empty:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")
    source_url = book_source_index().get(str(book_id))
    result = {"book_id": book_id, "source_url": source_url,
              "preview_url": None, "web_reader_url": None,
              "viewability": "UNKNOWN", "is_full_readable": False,
              "verification": "unavailable"}
    volume_id = google_books_volume_id(source_url)
    if volume_id:
        try:
            result.update(google_books_access(volume_id))
            result["verification"] = "google_books_api"
        except Exception:
            result["verification"] = "metadata_unavailable"
    return result


# =============================================================================
# PERSONALIZED LEARNING (ASSESSMENT DRIVEN; NO EMPLOYEE DATA PERSISTENCE)
# =============================================================================
from src.personalized_learning import calculate_gaps, merge_learning_recommendations
from src.hybrid_retrieval import HybridCatalogRetriever
from functools import lru_cache

@lru_cache(maxsize=1)
def get_hybrid_retriever():
    return HybridCatalogRetriever(recommender, FALLBACK_MODEL_DIR)

class AssessmentCompetency(BaseModel):
    competency_id: str = Field(..., examples=['C023'])
    current_level: float = Field(..., ge=0, description='Nilai hasil asesmen')
    required_level: float = Field(..., ge=0, description='Standar jabatan')
    importance: float = Field(3, ge=1, le=5, description='Prioritas jabatan; asumsi 1–5')

class PersonalizedRequest(BaseModel):
    assessment_source: Literal["simulasi", "hasil_asesmen_resmi"] = "simulasi"
    assessments: list[AssessmentCompetency] = Field(..., min_length=1, max_length=67)
    scale_max: float = Field(5, gt=0, le=100)
    top_k: int = Field(10, ge=1, le=20)
    categories: list[str] | None = None
    retrieval_mode: Literal["dense", "hybrid"] = "dense"

@app.post('/api/v1/personalized-learning', tags=['Rekomendasi e-Library'])
def personalized_learning(req: PersonalizedRequest):
    """Identifikasi gap skor aktual-target dan peringkat buku lintas kompetensi.

    Tidak menggunakan/menyimpan nama, NIP, atau data personal. Skema skor adalah
    asumsi demonstrasi sampai standar asesmen organisasi disepakati.
    """
    names = dict(zip(recommender.profiles['competency_id'], recommender.profiles['competency_name']))
    try:
        gaps = calculate_gaps([x.model_dump() for x in req.assessments], names, scale_max=req.scale_max)
        if req.retrieval_mode == 'hybrid':
            if recommender.model_name != 'bge_m3':
                raise ValueError('Hybrid RRF membutuhkan artefak BGE-M3 sebagai model utama')
            hybrid = get_hybrid_retriever()
            fetch = lambda cid, top_k: hybrid.search(cid, top_k=top_k, categories=req.categories)
        else:
            fetch = lambda cid, top_k: recommender.recommend_books_for_competency(
                cid, top_k=top_k, categories=req.categories)
        books = merge_learning_recommendations(
            gaps, fetch,
            top_k=req.top_k,
        )
        for book in books:
            book['source_url'] = book_source_index().get(str(book['book_id']))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {'status': 'success', 'gap_count': len(gaps),
            'gaps': [vars(x) for x in gaps], 'books': books,
            'method': 'weighted_competency_gap_and_' + req.retrieval_mode + '_retrieval',
            'assessment_source': req.assessment_source,
            'assessment_note': ('Simulasi ilustratif, bukan hasil asesmen organisasi.' if req.assessment_source == 'simulasi' else 'Angka diinput pengguna dari dokumen asesmen; sistem tidak memvalidasi keaslian atau standar jabatan.'),
            'disclaimer': ('Rekomendasi berbasis relevansi semantik dan skor kebutuhan belajar, '
                           'bukan bukti peningkatan kompetensi. Periksa kesesuaian bahan bacaan.')}


# =============================================================================
# SIMULASI COMPETENCY GAP (USER 1, USER 2, USER 3 DEMONSTRATION)
# =============================================================================

@app.get('/api/v1/simulation/profiles', tags=['Simulasi Competency Gap'])
def get_simulation_profiles():
    """Mengambil daftar 3 profil dummy karyawan untuk simulasi demonstrasi."""
    return {"status": "success", "profiles": SIMULATION_PROFILES}


@app.get('/api/v1/simulation/recommend/{user_id}', tags=['Simulasi Competency Gap'])
def get_simulation_recommendation(
    user_id: str,
    retrieval_mode: Literal["dense", "hybrid"] = Query("dense", description="Mode retrieval AI (dense BGE-M3 atau hybrid RRF)"),
    top_k: int = Query(6, ge=1, le=12)
):
    """Menjalankan rekomendasi berbasis competency gap untuk profil user terpilih (User 1, 2, atau 3)."""
    names = dict(zip(recommender.profiles['competency_id'], recommender.profiles['competency_name']))
    names['C057'] = "Machine Learning (IT Software Dev)"
    names['C065'] = "Data Management"
    names['ML_EVAL'] = "Evaluasi Model Machine Learning"
    names['MLOPS'] = "MLOps & Arsitektur AI Lanjutan"

    # Muat vektor simulasi pra-komputasi untuk ML, Evaluasi Model, dan MLOps
    sim_dense_path = ROOT / "models" / "simulation_vectors.npz"
    sim_tfidf_path = ROOT / "models" / "simulation_tfidf_vectors.npz"
    sim_dense = np.load(sim_dense_path) if sim_dense_path.exists() else None
    sim_tfidf = np.load(sim_tfidf_path) if sim_tfidf_path.exists() else None
    cat_vecs = np.load(recommender.artifact_dir / "catalog_vectors.npy")

    key_map = {"C057": "ML_FOUNDATION", "ML_EVAL": "ML_EVAL", "MLOPS": "MLOPS"}

    if retrieval_mode == 'hybrid':
        if recommender.model_name != 'bge_m3':
            raise HTTPException(status_code=400, detail='Hybrid RRF membutuhkan model utama BGE-M3')
        hybrid = get_hybrid_retriever()

        def fetch(cid, top_k=10):
            if sim_dense and sim_tfidf and cid in key_map:
                k = key_map[cid]
                dense = np.dot(cat_vecs, sim_dense[k])
                lexical = cosine_similarity(hybrid.catalog_vectors, sim_tfidf[k].reshape(1, -1)).ravel()
                dense_order = np.argsort(-dense)
                lex_order = np.argsort(-lexical)
                rrf = np.zeros(len(recommender.catalog))
                for o in (dense_order, lex_order):
                    for rank, idx in enumerate(o, 1):
                        rrf[idx] += 1 / (60 + rank)
                top_indices = np.argsort(-rrf)[:top_k]
                res = []
                for rank, idx in enumerate(top_indices, 1):
                    row = recommender.catalog.iloc[idx]
                    res.append({
                        'rank': rank,
                        'book_id': str(row['book_id']),
                        'judul': str(row['judul']),
                        'author': str(row.get('author', '')),
                        'tahun': str(row.get('tahun', '')),
                        'kategori': str(row.get('kategori_buku', '')),
                        'score': round(float(dense[idx]), 4),
                        'skor_model': round(float(dense[idx]), 4),
                        'rrf_score': round(float(rrf[idx]), 5),
                        'lexical_score': round(float(lexical[idx]), 4),
                        'model': 'hybrid_rrf_bge_m3_tfidf'
                    })
                return res
            return hybrid.search(cid, top_k=top_k)
    else:
        def fetch(cid, top_k=10):
            if sim_dense and cid in key_map:
                k = key_map[cid]
                dense = np.dot(cat_vecs, sim_dense[k])
                top_indices = np.argsort(-dense)[:top_k]
                res = []
                for rank, idx in enumerate(top_indices, 1):
                    row = recommender.catalog.iloc[idx]
                    res.append({
                        'rank': rank,
                        'book_id': str(row['book_id']),
                        'judul': str(row['judul']),
                        'author': str(row.get('author', '')),
                        'tahun': str(row.get('tahun', '')),
                        'kategori': str(row.get('kategori_buku', '')),
                        'score': round(float(dense[idx]), 4),
                        'skor_model': round(float(dense[idx]), 4),
                        'model': 'bge_m3_precomputed'
                    })
                return res
            return recommender.recommend_books_for_competency(cid, top_k=top_k)

    try:
        res = run_simulation_recommendation(
            user_id,
            fetch,
            names,
            top_k=top_k,
            retrieval_mode=retrieval_mode
        )
        for book in res['books']:
            book_id = str(book['book_id'])
            book['source_url'] = book_source_index().get(book_id)
            vol_id = google_books_volume_id(book['source_url'])
            if vol_id:
                book['google_id'] = vol_id
                book['embed_url'] = f"https://books.google.com/books?id={vol_id}&printsec=frontcover&output=embed"
                book['reader_url'] = f"https://books.google.com/books?id={vol_id}&printsec=frontcover"
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res['retrieval_mode'] = retrieval_mode
    return res


# =============================================================================
# AUTENTIKASI SESI PENGGUNA (USER 1, USER 2, USER 3)
# =============================================================================
AUTH_USERS = {
    "user1": {
        "id": "user_1",
        "username": "user1",
        "password": "password",
        "name": "User 1",
        "current_role": "Junior Data Scientist",
        "target_role": "Pratama Data Scientist",
        "scenario_type": "single_gap",
        "scenario_badge": "1 Competency Gap",
        "top_gap_summary": "Kesenjangan Utama: Data Analytics (Gap 1) — Membutuhkan penguatan analitik menuju level Pratama."
    },
    "user2": {
        "id": "user_2",
        "username": "user2",
        "password": "password",
        "name": "User 2",
        "current_role": "Junior Data Analyst",
        "target_role": "Pratama Data Scientist",
        "scenario_type": "multi_gap",
        "scenario_badge": "3 Competency Gaps",
        "top_gap_summary": "Gap tertinggi Anda: Machine Learning (Gap 3) — Disusul Risk Management (Gap 2) dan Data Analytics (Gap 1)."
    },
    "user3": {
        "id": "user_3",
        "username": "user3",
        "password": "password",
        "name": "User 3",
        "current_role": "Pratama Data Scientist",
        "target_role": "Pratama Data Scientist (Pengembangan Lanjutan)",
        "scenario_type": "zero_gap",
        "scenario_badge": "0 Gap · Upskilling & Pengayaan",
        "top_gap_summary": "Seluruh standar kompetensi terpenuhi (Gap 0) — Program Aktif: Upskilling Lanjutan (Evaluasi Model Machine Learning & MLOps)."
    },
    "user4": {
        "id": "user_4",
        "username": "user4",
        "password": "password",
        "name": "User 4",
        "current_role": "Junior Data Scientist",
        "target_role": "Pratama Data Scientist",
        "scenario_type": "single_gap",
        "scenario_badge": "1 Gap · Fokus Data Management",
        "top_gap_summary": "Kesenjangan Utama: Data Management (Gap 3) — Seluruh kompetensi lain telah terpenuhi (Gap 0); sistem merekomendasikan bahan bacaan terstruktur untuk mulai mempelajari tata kelola data."
    }
}

class LoginRequest(BaseModel):
    username: str
    password: Optional[str] = "password"

@app.post('/api/v1/auth/login', tags=['Autentikasi Sesi'])
def login(req: LoginRequest):
    u = req.username.strip().lower()
    user = AUTH_USERS.get(u)
    if not user:
        for cand in AUTH_USERS.values():
            if cand['id'] == u or cand['name'].lower() == u:
                user = cand
                break
    if not user:
        raise HTTPException(status_code=401, detail="Akun tidak ditemukan. Gunakan user1, user2, user3, atau user4.")
    return {
        "status": "success",
        "session_token": f"session-{user['id']}",
        "user": user
    }


# Jalankan server setelah SEMUA endpoint didaftarkan (penting saat python api.py).
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"),
                port=int(os.environ.get("PORT", "8000")), reload=False)
