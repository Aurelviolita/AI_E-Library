"""Perencanaan pembelajaran dari skor asesmen; bukan prediksi peningkatan kompetensi.

Semua skor asesmen dikirim per permintaan. Modul ini tidak menyimpan data pegawai.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Gap:
    competency_id: str
    competency_name: str
    current_level: float
    required_level: float
    gap: float
    priority: float


def calculate_gaps(items: list[dict], names: dict[str, str], *, scale_max: float = 5.0) -> list[Gap]:
    """Gap=max(target-actual,0); priority=normalized gap * importance (1..5)."""
    if not 0 < scale_max <= 100:
        raise ValueError('scale_max harus > 0 dan <= 100')
    seen = set()
    results = []
    for item in items:
        cid = str(item['competency_id']).strip()
        if cid not in names:
            raise ValueError(f'Kompetensi tidak ditemukan: {cid}')
        if cid in seen:
            raise ValueError(f'Kompetensi duplikat: {cid}')
        seen.add(cid)
        actual, target = float(item['current_level']), float(item['required_level'])
        weight = float(item.get('importance', 3))
        if not 0 <= actual <= scale_max or not 0 <= target <= scale_max:
            raise ValueError(f'Skor {cid} harus berada dalam rentang 0 sampai {scale_max}')
        if not 1 <= weight <= 5:
            raise ValueError('importance harus 1 sampai 5')
        gap = max(target - actual, 0.0)
        if gap:
            results.append(Gap(cid, names[cid], actual, target, round(gap, 4), round(gap / scale_max * weight, 4)))
    return sorted(results, key=lambda g: (-g.priority, -g.gap, g.competency_id))


def merge_learning_recommendations(gaps: list[Gap], fetch_books, *, top_k: int = 10, per_competency: int = 10):
    """Gabungkan buku dari beberapa gap. Dedup berdasarkan book_id; skor similarity bukan probabilitas.

    Skor peringkat dinormalisasi per-query dengan min-max untuk membandingkan prioritas.
    Tidak diasumsikan skor lintas kompetensi terkalibrasi.
    """
    if not gaps:
        return []
    best = {}
    max_priority = max(g.priority for g in gaps)
    for gap in gaps:
        books = fetch_books(gap.competency_id, top_k=per_competency)
        if not books:
            continue
        values = [float(b['score']) for b in books]
        lo, hi = min(values), max(values)
        for book in books:
            relevance = (float(book['score']) - lo) / (hi - lo) if hi > lo else 1.0
            # 70% relevansi dalam satu kompetensi + 30% urgensi gap.
            priority_score = gap.priority / max_priority
            combined = round(0.7 * relevance + 0.3 * priority_score, 4)
            bid = str(book['book_id'])
            why = (f"Mendukung kompetensi {gap.competency_name} ({gap.competency_id}); "
                   f"tingkat saat ini {gap.current_level:g}, target {gap.required_level:g}, "
                   f"selisih {gap.gap:g}. Kecocokan judul/abstrak perlu ditinjau pengguna.")
            rec = {
                **book,
                'raw_score': round(float(book.get('raw_score') or book.get('skor_model') or book.get('score', 0.0)), 4),
                'cosine_similarity': round(float(book.get('raw_score') or book.get('skor_model') or book.get('score', 0.0)), 4),
                'rrf_score': round(float(book.get('rrf_score', 0.0)), 5) if 'rrf_score' in book else None,
                'personalized_score': combined,
                'relevance_weight': round(relevance, 4),
                'gap_priority_weight': round(priority_score, 4),
                'reason': why,
                'target_competency_id': gap.competency_id,
                'gap_priority': gap.priority,
                'score_interpretation': 'Skor gabungan terbobot: 70% relevansi konten semantik + 30% urgensi kesenjangan kompetensi'
            }
            if bid not in best or combined > best[bid]['personalized_score']:
                best[bid] = rec
    ordered = sorted(best.values(), key=lambda b: (-b['personalized_score'], str(b['book_id'])))
    return [{**b, 'rank': idx} for idx, b in enumerate(ordered[:top_k], 1)]
