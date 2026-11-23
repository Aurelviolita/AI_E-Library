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
        "scenario_title": "Satu Competency Gap",
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
        "narrative": "Pratama Data Scientist telah memenuhi semua standar kompetensi jabatannya (Gap = 0). Sistem tidak memilih buku secara acak, melainkan memberikan rekomendasi terarah untuk materi lanjutan Data Analytics & Machine Learning.",
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
            {"competency_id": "C066", "competency_name": "Data Analytics", "topic": "Materi Lanjutan Analytics & AI"},
            {"competency_id": "C057", "competency_name": "Machine Learning", "topic": "Arsitektur Algoritma Lanjutan"}
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
            else:
                comp_display = comp_name

            # Temukan gap info
            gap_item = next((g for g in gaps if g.competency_id == comp_id), None)
            if gap_item:
                b["reason"] = (
                    f"Rekomendasi prioritas untuk menutup gap kompetensi {comp_display}: "
                    f"nilai aktual {gap_item.current_level:g} menuju target {gap_item.required_level:g} "
                    f"(selisih gap {gap_item.gap:g}, bobot prioritas {gap_item.priority:.2f})."
                )
            b["target_competency_name"] = comp_display

        return {
            "status": "success",
            "profile": profile,
            "scenario_type": scenario_type,
            "is_upskilling": False,
            "gap_count": len(gaps),
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
        upskilling_tracks = profile.get("upskilling_tracks", [
            {"competency_id": "C066", "competency_name": "Data Analytics", "topic": "Materi Lanjutan Analytics"},
            {"competency_id": "C057", "competency_name": "Machine Learning", "topic": "Arsitektur Algoritma"}
        ])

        all_books = []
        seen_bids = set()
        per_track = max(3, top_k // len(upskilling_tracks))

        for track in upskilling_tracks:
            cid = track["competency_id"]
            comp_name = track["competency_name"]
            fetched = fetch_books(cid, per_track + 2)
            for b in fetched:
                bid = str(b["book_id"])
                if bid not in seen_bids:
                    seen_bids.add(bid)
                    rec = dict(b)
                    rec["target_competency_id"] = cid
                    rec["target_competency_name"] = comp_name
                    rec["reason"] = (
                        f"Program Pengayaan (Upskilling): Seluruh standar kompetensi jabatan sudah terpenuhi (Gap = 0). "
                        f"Buku ini direkomendasikan untuk pendalaman materi lanjutan pada {comp_name}."
                    )
                    rec["personalized_score"] = round(float(b.get("score", 0.6)), 4)
                    all_books.append(rec)

        # Urutkan berdasarkan skor semantik BGE-M3
        all_books.sort(key=lambda x: -x["personalized_score"])
        selected_books = [{**b, "rank": idx} for idx, b in enumerate(all_books[:top_k], 1)]

        return {
            "status": "success",
            "profile": profile,
            "scenario_type": "zero_gap",
            "is_upskilling": True,
            "gap_count": 0,
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
            "summary_note": "Semua standar kompetensi telah terpenuhi (Gap = 0). Menampilkan rekomendasi upskilling materi lanjutan Data Analytics & Machine Learning."
        }
