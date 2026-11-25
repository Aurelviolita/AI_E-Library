"""Simulasi AI e-Library: Sistem Rekomendasi Berbasis Competency Gap.

Menyediakan data tetap 3 profil karyawan untuk demonstrasi:
1. User 1: 1 Competency Gap (Junior Data Scientist -> Pratama Data Scientist)
2. User 2: 3 Competency Gap dengan prioritas 3, 2, 1 (Junior Data Analyst -> Pratama Data Scientist)
3. User 3: 0 Gap / Upskilling Materi Lanjutan (Pratama Data Scientist)
"""
from __future__ import annotations
from typing import Any, Callable, Literal
from src.personalized_learning import Gap, calculate_gaps, merge_learning_recommendations

SIMULATION_PROFILES: list[dict[str, Any]] = [
    {
        "id": "user_1",
        "name": "User 1",
        "current_role": "Junior Data Scientist",
        "target_role": "Pratama Data Scientist",
        "scenario_type": "single_gap",
        "scenario_badge": "1 Competency Gap",
        "scenario_title": "Satu Competency Gap (Data Analytics)",
        "top_gap_summary": "Kesenjangan Utama Anda: Data Analytics (Gap 1) — Membutuhkan penguatan analitik menuju level Pratama.",
        "narrative": "Junior Data Scientist ingin naik ke Pratama Data Scientist. Hasil asesmen menunjukkan Data Analytics bernilai 3, sedangkan targetnya 4 (Gap = 1). Sistem merekomendasikan buku untuk memperkuat Data Analytics.",
        "assessments": [
            {
                "competency_id": "C066",
                "competency_name": "Data Analytics",
                "current_level": 3.0,
                "required_level": 4.0,
                "importance": 4.0,
                "gap": 1.0,
                "priority_label": "Prioritas Pengembangan",
                "notes": "Target jabatan Pratama Data Scientist membutuhkan penguasaan analitik tingkat 4."
            }
        ]
    },
    {
        "id": "user_2",
        "name": "User 2",
        "current_role": "Junior Data Analyst",
        "target_role": "Pratama Data Scientist",
        "scenario_type": "multi_gap",
        "scenario_badge": "3 Competency Gaps",
        "scenario_title": "Tiga Competency Gap (Multi-Gap Berbobot)",
        "top_gap_summary": "Gap tertinggi Anda: Machine Learning (Gap 3) — Disusul Risk Management (Gap 2) dan Data Analytics (Gap 1). Rekomendasi di bawah memprioritaskan penutupan gap terbesar.",
        "narrative": "Junior Data Analyst ingin beralih menjadi Pratama Data Scientist. Asesmen menunjukkan 3 gap: Machine Learning (Gap 3), Risk Management (Gap 2), dan Data Analytics (Gap 1). Sistem merekomendasikan buku terintegrasi dengan bobot prioritas Gap 3 > Gap 2 > Gap 1.",
        "assessments": [
            {
                "competency_id": "C057",
                "competency_name": "Machine Learning (IT Software Dev)",
                "current_level": 1.0,
                "required_level": 4.0,
                "importance": 5.0,
                "gap": 3.0,
                "priority_label": "Prioritas Sangat Tinggi (Gap 3)",
                "notes": "Fondasi algoritma dan implementasi Machine Learning sangat krusial untuk promosi."
            },
            {
                "competency_id": "C023",
                "competency_name": "Risk Management",
                "current_level": 2.0,
                "required_level": 4.0,
                "importance": 3.0,
                "gap": 2.0,
                "priority_label": "Prioritas Menengah (Gap 2)",
                "notes": "Mitigasi risiko operasional, kepatuhan, dan integritas data layanan kesehatan."
            },
            {
                "competency_id": "C066",
                "competency_name": "Data Analytics",
                "current_level": 3.0,
                "required_level": 4.0,
                "importance": 2.0,
                "gap": 1.0,
                "priority_label": "Prioritas Normal (Gap 1)",
                "notes": "Penyempurnaan analisis statistik dan eksperimen data."
            }
        ]
    },
    {
        "id": "user_3",
        "name": "User 3",
        "current_role": "Pratama Data Scientist",
        "target_role": "Pratama Data Scientist (Pengembangan Lanjutan)",
        "scenario_type": "zero_gap",
        "scenario_badge": "0 Gap · Upskilling & Pengayaan",
        "scenario_title": "Tidak Ada Gap (Pengayaan / Upskilling)",
        "top_gap_summary": "Seluruh standar kompetensi terpenuhi (Gap 0) — Program Aktif: Upskilling Lanjutan (Evaluasi Model Machine Learning & MLOps).",
        "narrative": "Pratama Data Scientist telah memenuhi semua standar kompetensi jabatannya (Gap = 0). Sistem tidak memilih buku secara acak, melainkan memberikan rekomendasi terarah untuk pengayaan topik lanjutan: Evaluasi Model Machine Learning dan MLOps & Arsitektur AI Lanjutan.",
        "assessments": [
            {
                "competency_id": "C066",
                "competency_name": "Data Analytics",
                "current_level": 4.0,
                "required_level": 4.0,
                "importance": 4.0,
                "gap": 0.0,
                "priority_label": "Standar Terpenuhi (Gap 0)",
                "notes": "Standar terpenuhi secara mandiri pada tugas kompleks dan proyek strategis."
            },
            {
                "competency_id": "C057",
                "competency_name": "Machine Learning (IT Software Dev)",
                "current_level": 4.0,
                "required_level": 4.0,
                "importance": 4.0,
                "gap": 0.0,
                "priority_label": "Standar Terpenuhi (Gap 0)",
                "notes": "Standar terpenuhi dalam rekayasa sistem pembelajaran mesin."
            },
            {
                "competency_id": "C023",
                "competency_name": "Risk Management",
                "current_level": 4.0,
                "required_level": 4.0,
                "importance": 3.0,
                "gap": 0.0,
                "priority_label": "Standar Terpenuhi (Gap 0)",
                "notes": "Standar tata kelola risiko terpenuhi sesuai standar organisasi."
            }
        ],
        "upskilling_tracks": [
            {
                "competency_id": "ML_EVAL",
                "competency_name": "Evaluasi Model Machine Learning",
                "topic": "Evaluasi Model & Diagnostic Metrics",
                "description": "Pengujian keandalan model, validasi silang (cross-validation), metrik diagnostik ROC-AUC, penanganan overfitting, dan validasi empiris performa model ML."
            },
            {
                "competency_id": "MLOPS",
                "competency_name": "MLOps & Arsitektur AI Lanjutan",
                "topic": "MLOps & Arsitektur Sistem AI Lanjutan",
                "description": "Deployment model ke produksi, continuous training pipelines, model monitoring, skalabilitas arsitektur sistem AI, dan automated CI/CD for ML."
            }
        ]
    },
    {
        "id": "user_4",
        "name": "User 4",
        "current_role": "Junior Data Scientist",
        "target_role": "Pratama Data Scientist",
        "scenario_type": "single_gap",
        "scenario_badge": "1 Gap · Fokus Data Management",
        "scenario_title": "Satu Competency Gap: Fondasi Data Management",
        "top_gap_summary": "Kesenjangan Utama: Data Management (Gap 3) — Seluruh kompetensi lain telah terpenuhi (Gap 0); sistem merekomendasikan bahan bacaan terstruktur untuk mulai mempelajari tata kelola data.",
        "narrative": "Junior Data Scientist ingin naik ke Pratama Data Scientist. Semua standar kompetensi dalam profil jabatannya sudah dikuasai dengan baik (Data Analytics dan Machine Learning bernilai 4 dari target 4, Gap = 0), kecuali Data Management yang bernilai 1 dari target 4 (Gap = 3). Mentor ingin melihat buku apa yang sistem pilih untuk membantu karyawan ini mulai belajar Data Management dari dasar.",
        "assessments": [
            {
                "competency_id": "C065",
                "competency_name": "Data Management",
                "current_level": 1.0,
                "required_level": 4.0,
                "importance": 5.0,
                "gap": 3.0,
                "priority_label": "Prioritas Utama (Mulai Belajar)",
                "notes": "Memerlukan pemahaman komprehensif mulai dari konsep data governance, master data, hingga manajemen basis data terintegrasi."
            },
            {
                "competency_id": "C066",
                "competency_name": "Data Analytics",
                "current_level": 4.0,
                "required_level": 4.0,
                "importance": 4.0,
                "gap": 0.0,
                "priority_label": "Standar Terpenuhi (Gap 0)",
                "notes": "Penguasaan teknik analisis data dan pemodelan statistik telah memenuhi standar mandiri."
            },
            {
                "competency_id": "C057",
                "competency_name": "Machine Learning (IT Software Dev)",
                "current_level": 4.0,
                "required_level": 4.0,
                "importance": 4.0,
                "gap": 0.0,
                "priority_label": "Standar Terpenuhi (Gap 0)",
                "notes": "Kemampuan implementasi model pembelajaran mesin telah memenuhi standar jabatan."
            }
        ]
    }
]

def get_simulation_profile(user_id: str) -> dict[str, Any] | None:
    """Mengambil satu profil simulasi berdasarkan id."""
    for p in SIMULATION_PROFILES:
        if p["id"] == user_id:
            return p
    return None

def run_simulation_recommendation(
    user_id: str,
    fetch_books: Callable[[str, int], list[dict[str, Any]]],
    names: dict[str, str],
    *,
    top_k: int = 8,
    retrieval_mode: str = "dense"
) -> dict[str, Any]:
    """Menjalankan rekomendasi buku berbasis gap untuk simulasi profil yang dipilih."""
    profile = get_simulation_profile(user_id)
    if not profile:
        raise ValueError(f"Profil simulasi tidak ditemukan: {user_id}")

    scenario_type = profile["scenario_type"]

    # Skenario 1 & 2: Ada gap kompetensi
    if scenario_type in ("single_gap", "multi_gap"):
        raw_items = [
            {
                "competency_id": a["competency_id"],
                "current_level": a["current_level"],
                "required_level": a["required_level"],
                "importance": a["importance"]
            }
            for a in profile["assessments"]
        ]
        gaps = calculate_gaps(raw_items, names, scale_max=5.0)
        books = merge_learning_recommendations(gaps, fetch_books, top_k=top_k)

        # Perjelas alasan rekomendasi untuk masing-masing kompetensi
        for b in books:
            comp_id = b.get("target_competency_id", "")
            comp_name = names.get(comp_id, comp_id)
            if comp_id == "C057":
                comp_display = "Machine Learning (IT Software Dev)"
            elif comp_id == "C065":
                comp_display = "Data Management"
            else:
                comp_display = comp_name

            # Temukan gap info
            gap_item = next((g for g in gaps if g.competency_id == comp_id), None)
            if gap_item:
                if user_id == "user_4" and comp_id == "C065":
                    b["reason"] = (
                        f"Rekomendasi prioritas untuk mulai mempelajari Data Management: "
                        f"nilai aktual {gap_item.current_level:g} menuju target {gap_item.required_level:g} "
                        f"(selisih gap {gap_item.gap:g}, bobot prioritas {gap_item.priority:.2f}). "
                        f"Buku ini dipilih untuk membantu membangun pemahaman tata kelola data (data governance), arsitektur data, dan master data management dari dasar."
                    )
                else:
                    b["reason"] = (
                        f"Rekomendasi prioritas untuk menutup gap kompetensi {comp_display}: "
                        f"nilai aktual {gap_item.current_level:g} menuju target {gap_item.required_level:g} "
                        f"(selisih gap {gap_item.gap:g}, bobot prioritas {gap_item.priority:.2f})."
                    )
            b["target_competency_name"] = comp_display
            b["retrieval_mode"] = retrieval_mode
            if retrieval_mode == "hybrid":
                rrf_val = float(b.get('rrf_score') or 0.032)
                raw_sc = float(b.get('raw_score') or b.get('score') or 0.0)
                b["score_label"] = "Skor Hybrid RRF"
                b["score_detail"] = f"RRF Score: {rrf_val:.5f} | Cosine Semantik: {raw_sc:.3f}"
            else:
                raw_sc = float(b.get('raw_score') or b.get('score') or 0.0)
                b["score_label"] = "Skor BGE-M3 (Semantik)"
                b["score_detail"] = f"Cosine Similarity: {raw_sc:.3f} (Kemiripan semantik representasi profil)"

        return {
            "status": "success",
            "profile": profile,
            "scenario_type": scenario_type,
            "is_upskilling": False,
            "retrieval_mode": retrieval_mode,
            "gap_count": len(gaps),
            "top_gap_summary": profile.get("top_gap_summary", ""),
            "gaps": [
                {
                    "competency_id": g.competency_id,
                    "competency_name": "Machine Learning (IT Software Dev)" if g.competency_id == "C057" else g.competency_name,
                    "current_level": g.current_level,
                    "required_level": g.required_level,
                    "gap": g.gap,
                    "priority": g.priority
                }
                for g in gaps
            ],
            "books": books,
            "summary_note": f"Berhasil menghitung {len(gaps)} kesenjangan kompetensi dan merekomendasikan {len(books)} buku terkait."
        }

    # Skenario 3: Zero Gap (Upskilling & Materi Lanjutan)
    else:
        upskilling_tracks = profile.get("upskilling_tracks", [])
        all_books = []
        seen_bids = set()
        per_track = max(3, top_k // len(upskilling_tracks)) if upskilling_tracks else top_k

        for track in upskilling_tracks:
            cid = track["competency_id"]
            comp_name = track["competency_name"]
            topic_name = track.get("topic", comp_name)
            desc = track.get("description", "")
            fetched = fetch_books(cid, per_track + 2)
            for b in fetched:
                bid = str(b["book_id"])
                if bid not in seen_bids:
                    seen_bids.add(bid)
                    rec = dict(b)
                    rec["target_competency_id"] = cid
                    rec["target_competency_name"] = f"{comp_name}"
                    rec["topic_label"] = topic_name
                    rec["reason"] = (
                        f"Program Pengayaan Lanjutan (Upskilling): Seluruh standar kompetensi jabatan telah terpenuhi (Gap = 0). "
                        f"Buku ini direkomendasikan secara khusus untuk pendalaman topik lanjutan '{topic_name}': {desc}"
                    )
                    raw_sc = round(float(b.get("score", 0.6)), 4)
                    rec["raw_score"] = raw_sc
                    rec["cosine_similarity"] = raw_sc
                    rec["rrf_score"] = round(float(b.get("rrf_score", 0.0)), 5) if 'rrf_score' in b else None
                    rec["personalized_score"] = raw_sc
                    rec["retrieval_mode"] = retrieval_mode
                    if retrieval_mode == "hybrid":
                        rec["score_label"] = "Skor Hybrid RRF"
                        rec["score_detail"] = f"RRF: {rec.get('rrf_score', 0.032):.5f} | Cosine: {raw_sc:.3f}"
                    else:
                        rec["score_label"] = "Skor BGE-M3 (Semantik)"
                        rec["score_detail"] = f"Cosine Similarity: {raw_sc:.3f} (Kemiripan semantik materi)"
                    all_books.append(rec)

        # Urutkan berdasarkan skor
        if retrieval_mode == "hybrid":
            all_books.sort(key=lambda x: -float(x.get("rrf_score") or x.get("raw_score") or 0))
        else:
            all_books.sort(key=lambda x: -float(x.get("raw_score") or 0))

        selected_books = [{**b, "rank": idx} for idx, b in enumerate(all_books[:top_k], 1)]

        return {
            "status": "success",
            "profile": profile,
            "scenario_type": "zero_gap",
            "is_upskilling": True,
            "retrieval_mode": retrieval_mode,
            "gap_count": 0,
            "top_gap_summary": profile.get("top_gap_summary", ""),
            "gaps": [
                {
                    "competency_id": a["competency_id"],
                    "competency_name": a["competency_name"],
                    "current_level": a["current_level"],
                    "required_level": a["required_level"],
                    "gap": 0.0,
                    "priority": 0.0
                }
                for a in profile["assessments"]
            ],
            "books": selected_books,
            "summary_note": "Semua standar kompetensi telah terpenuhi (Gap = 0). Menampilkan rekomendasi upskilling materi lanjutan Evaluasi Model Machine Learning & MLOps."
        }
