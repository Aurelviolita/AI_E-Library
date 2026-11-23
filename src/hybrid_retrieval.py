"""Hybrid ranking BGE-M3 + TF-IDF (RRF), tanpa mengubah model pretrained.

BGE-M3 dense vectors berasal dari model yang telah diekspor; TF-IDF dipakai untuk
mengurangi kehilangan istilah teknis yang tepat. Bukan reranker neural.
"""
from pathlib import Path
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
import joblib

class HybridCatalogRetriever:
    def __init__(self, recommender, tfidf_dir: str | Path, rrf_k: int = 60):
        self.base = recommender
        path = Path(tfidf_dir)
        self.vectorizer = joblib.load(path / 'tfidf_vectorizer.joblib')
        self.catalog_vectors = self.vectorizer.transform((recommender.catalog['judul'].astype(str) + '. ' + recommender.catalog['abstrak'].astype(str)).tolist())
        self.comp_vectors = self.vectorizer.transform(recommender.profiles['teks_profil_lengkap'].astype(str).tolist())
        if self.catalog_vectors.shape[0] != len(recommender.catalog):
            raise ValueError('Urutan/jumlah katalog TF-IDF tidak sama; fusion dibatalkan')
        if self.catalog_vectors.shape[1] != self.comp_vectors.shape[1]:
            raise ValueError('Dimensi TF-IDF katalog dan kompetensi tidak konsisten')
        if self.comp_vectors.shape[0] != len(recommender.profiles):
            raise ValueError('Urutan/jumlah kompetensi TF-IDF tidak sama; fusion dibatalkan')
        self.rrf_k = rrf_k

    def search(self, competency_id: str, *, top_k: int = 10, categories: list[str] | None = None):
        # Ambil full ranking dari dua representasi; RRF tidak membandingkan skala cosine.
        ids = self.base.profiles.index[self.base.profiles['competency_id'] == str(competency_id)].tolist()
        if not ids:
            raise KeyError(f'Kompetensi tidak ditemukan: {competency_id}')
        idx = ids[0]
        dense = np.load(self.base.artifact_dir / 'catalog_vectors.npy', mmap_mode='r') @ self.base.competency_vectors[idx]
        lexical = cosine_similarity(self.catalog_vectors, self.comp_vectors[idx]).ravel()
        if categories:
            eligible = np.flatnonzero(self.base.catalog['kategori_buku'].isin(categories).to_numpy())
        else:
            eligible = np.arange(len(self.base.catalog))
        if len(eligible) == 0:
            return []
        dense_order = eligible[np.argsort(-dense[eligible], kind='stable')]
        lexical_order = eligible[np.argsort(-lexical[eligible], kind='stable')]
        scores = np.zeros(len(self.base.catalog), dtype=float)
        for ranking in (dense_order, lexical_order):
            for rank, book_idx in enumerate(ranking, 1):
                scores[book_idx] += 1 / (self.rrf_k + rank)
        order = eligible[np.argsort(-scores[eligible], kind='stable')[:top_k]]
        out = []
        for rank, i in enumerate(order, 1):
            book = self.base.catalog.iloc[int(i)]
            out.append({
                'rank': rank, 'book_id': str(book['book_id']), 'judul': str(book['judul']),
                'author': str(book.get('author','')), 'tahun': str(book.get('tahun','')),
                'kategori': str(book.get('kategori_buku','')),
                'score': round(float(scores[i]), 6),
                'skor_model': round(float(dense[i]), 4),
                'rrf_score': round(float(scores[i]), 5),
                'raw_score': round(float(dense[i]), 4),
                'lexical_score': round(float(lexical[i]), 4),
                'model': 'hybrid_rrf_bge_m3_tfidf', 'is_fallback': False,
                'query_latency_ms': None,
            })
        return out
