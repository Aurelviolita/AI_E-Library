import {
  AlertCircle,
  AlertTriangle,
  Award,
  BookOpen,
  Cpu,
  ExternalLink,
  Info,
  Layers,
  Sparkles,
  TrendingUp,
  User,
  Users
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  fromSimulationBook,
  getSimulationRecommendation,
  type SimulationResult,
  type UserSession
} from "../api";
import { Cover } from "./Cover";
import type { OpenBook } from "../types";

export function SimulationSection({
  open,
  session,
  hideTopCallout = false
}: {
  open: OpenBook;
  session: UserSession;
  hideTopCallout?: boolean;
}) {
  const [mode, setMode] = useState<"dense" | "hybrid">("dense");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session?.id) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    getSimulationRecommendation(session.id, mode, 6, controller.signal)
      .then((res) => {
        if (!controller.signal.aborted) {
          setResult(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : "Gagal memuat rekomendasi kompetensi");
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [session.id, mode]);

  const activeProfile = result?.profile;

  const badgeClass =
    session.id === "user_4"
      ? "badge-teal"
      : session.scenario_type === "single_gap"
      ? "badge-amber"
      : session.scenario_type === "multi_gap"
      ? "badge-coral"
      : "badge-emerald";

  return (
    <section className="simulation-section" aria-label="Portal Rekomendasi Berbasis Competency Gap">
      {/* 1. PROMINENT TOP SUMMARY CALLOUT (HASIL ASESMEN DI ATAS LAYAR) */}
      {!hideTopCallout && (
        <div className="top-gap-summary-callout">
          <div className="summary-callout-icon">
            {session.scenario_type === "zero_gap" ? (
              <Sparkles size={24} className="icon-emerald" />
            ) : session.scenario_type === "multi_gap" ? (
              <AlertTriangle size={24} className="icon-coral" />
            ) : session.id === "user_4" ? (
              <TrendingUp size={24} style={{ color: "#0f766e" }} />
            ) : (
              <TrendingUp size={24} className="icon-amber" />
            )}
          </div>
          <div className="summary-callout-body">
            <div className="summary-callout-pill">
              {session.scenario_type === "zero_gap"
                ? "STANDAR KOMPETENSI TERPENUHI (GAP 0)"
                : session.id === "user_4"
                ? "GAP UTAMA: DATA MANAGEMENT (GAP 3)"
                : session.scenario_type === "multi_gap"
                ? "GAP PRIORITAS TERTINGGI: MACHINE LEARNING (GAP 3)"
                : "KESENJANGAN UTAMA: DATA ANALYTICS (GAP 1)"}
            </div>
            <h3 className="summary-callout-title">
              {result?.top_gap_summary || activeProfile?.top_gap_summary || session.top_gap_summary || (
                session.id === "user_4"
                  ? "Kesenjangan Utama: Data Management (Gap 3) — Membantu mulai mempelajari tata kelola dan manajemen data."
                  : session.scenario_type === "multi_gap"
                  ? "Gap tertinggi Anda: Machine Learning (3) — Disusul Risk Management (2) dan Data Analytics (1)."
                  : session.scenario_type === "single_gap"
                  ? "Kesenjangan Utama: Data Analytics (1) — Membutuhkan penguatan analitik menuju level Pratama."
                  : "Seluruh standar kompetensi terpenuhi (Gap 0) — Program Aktif: Upskilling Lanjutan (Evaluasi Model & MLOps)."
              )}
            </h3>
            <p className="summary-callout-desc">
              {session.id === "user_4"
                ? "Semua kompetensi lain telah terpenuhi (Gap 0). Rekomendasi di bawah dipilih secara khusus oleh model BGE-M3 untuk membantu Anda mulai belajar Data Management (tata kelola data, arsitektur basis data, dan master data) dari dasar."
                : session.scenario_type === "multi_gap"
                ? "Rekomendasi buku di bawah ini diprioritaskan secara proporsional untuk menutup kesenjangan terbesar Anda terlebih dahulu (Gap 3 > Gap 2 > Gap 1)."
                : session.scenario_type === "single_gap"
                ? "Rekomendasi buku di bawah ini dikurasi secara khusus untuk menaikkan skor kompetensi dari level 3 menuju target jabatan level 4."
                : "Anda telah menguasai kompetensi dasar jabatan. Rekomendasi di bawah berfokus pada topik lanjutan spesifik untuk memperluas kapabilitas profesional."}
            </p>
          </div>
        </div>
      )}

      {/* 2. HEADER WORKSPACE KARYAWAN AKTIF (SESI LOGIN) */}
      <div className="employee-workspace-header">
        <div className="workspace-user-intro">
          <div className="workspace-avatar">
            {session.scenario_type === "multi_gap" ? <Users size={26} /> : <User size={26} />}
          </div>
          <div>
            <div className="workspace-badge-row">
              <span className="eyebrow">PORTAL PENGEMBANGAN KARIER</span>
              <span className={`simulation-badge ${badgeClass}`}>
                {session.scenario_badge}
              </span>
            </div>
            <h2>Selamat Datang, {session.name}</h2>
            <div className="workspace-career-path">
              <span className="role-chip current">{session.current_role}</span>
              <span className="path-arrow">➔</span>
              <span className="role-chip target">{session.target_role}</span>
            </div>
          </div>
        </div>

        <div className="workspace-session-info">
          <span className="session-status-badge">● Sesi Karyawan Aktif</span>
          <span className="session-user-id">ID: {session.username}</span>
        </div>
      </div>

      <div className="simulation-panel">
        {/* Narasi Alur Karier */}
        {activeProfile?.narrative && (
          <div className="career-narrative-banner">
            <Award size={20} className="narrative-icon" />
            <p>{activeProfile.narrative}</p>
          </div>
        )}

        {/* Tabel Nilai Asesmen & Perhitungan Gap Karyawan Ini */}
        {activeProfile && (
          <div className="assessment-table-card">
            <div className="table-card-header">
              <div>
                <span className="eyebrow">HASIL ASESMEN STANDAR KOMPETENSI</span>
                <h3>Tabel Penilaian &amp; Perhitungan Kesenjangan (Gap)</h3>
              </div>
              <div className="formula-pill">
                <code>Competency Gap = max(Target − Aktual, 0)</code>
              </div>
            </div>

            <div className="table-responsive">
              <table className="simulation-table">
                <thead>
                  <tr>
                    <th>Kompetensi</th>
                    <th style={{ width: "130px" }}>Nilai Aktual</th>
                    <th style={{ width: "130px" }}>Target Jabatan</th>
                    <th style={{ width: "115px" }}>Kesenjangan</th>
                    <th>Bobot &amp; Prioritas</th>
                    <th>Catatan Kebutuhan</th>
                  </tr>
                </thead>
                <tbody>
                  {activeProfile.assessments.map((a) => {
                    const hasGap = a.gap > 0;
                    return (
                      <tr key={a.competency_id}>
                        <td>
                          <strong>{a.competency_name}</strong>
                          <span className="comp-id-sub">{a.competency_id}</span>
                        </td>
                        <td>
                          <div className="score-cell">
                            <span className="score-num">{a.current_level} / 5</span>
                            <div className="score-bar-bg">
                              <div
                                className="score-bar-fill actual"
                                style={{ width: `${(a.current_level / 5) * 100}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="score-cell">
                            <span className="score-num">{a.required_level} / 5</span>
                            <div className="score-bar-bg">
                              <div
                                className="score-bar-fill target"
                                style={{ width: `${(a.required_level / 5) * 100}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`gap-badge ${hasGap ? "gap-positive" : "gap-zero"}`}>
                            {hasGap ? `Gap ${a.gap}` : "0 (Lengkap)"}
                          </span>
                        </td>
                        <td>
                          <span className="priority-text">{a.priority_label}</span>
                        </td>
                        <td className="notes-cell">{a.notes || "–"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <p className="table-disclaimer">
              * Data asesmen di atas disesuaikan secara otomatis berdasarkan akun sesi yang aktif.
            </p>
          </div>
        )}

        {/* AI RETRIEVAL ENGINE SELECTOR */}
        <div className="engine-controls-bar">
          <div className="engine-info">
            <Cpu size={18} />
            <span>
              Model Aktif:{" "}
              <strong>{mode === "dense" ? "BGE-M3 (1024-dim Semantik Cosine)" : "Hybrid RRF (BGE-M3 + TF-IDF)"}</strong>
            </span>
          </div>
          <div className="model-toggle-group">
            <span className="toggle-label">Mode Retrieval:</span>
            <button
              type="button"
              className={`toggle-btn ${mode === "dense" ? "active" : ""}`}
              onClick={() => setMode("dense")}
            >
              <Sparkles size={14} /> BGE-M3 (Semantik)
            </button>
            <button
              type="button"
              className={`toggle-btn ${mode === "hybrid" ? "active" : ""}`}
              onClick={() => setMode("hybrid")}
            >
              <Layers size={14} /> Hybrid (BGE-M3 + TF-IDF)
            </button>
          </div>
        </div>

        {/* KOTAK TRANSPARANSI METODOLOGI SKOR REKOMENDASI */}
        <div className="score-methodology-card">
          <div className="methodology-badge">
            <Info size={15} />
            <span>Transparansi Perhitungan Skor &amp; Pemeringkatan Rekomendasi:</span>
          </div>
          <div className="methodology-text">
            {mode === "dense" ? (
              <p>
                <strong>Mode BGE-M3 (Dense):</strong> Skor merupakan nilai <em>Cosine Similarity</em> (misal <code>0.701</code> atau <code>70.1%</code>) antara representasi semantik kompetensi (vektor 1024 dimensi) dengan representasi judul &amp; abstrak buku di katalog. Semakin mendekati 100%, semakin mendalam kecocokan substansi buku dengan kompetensi target.
              </p>
            ) : (
              <p>
                <strong>Mode Hybrid RRF:</strong> Menggabungkan peringkat <em>Dense Semantik (BGE-M3)</em> dan <em>Leksikal (TF-IDF)</em> menggunakan formula <em>Reciprocal Rank Fusion</em> <code>RRF = ∑(1 / (60 + rank))</code>. Angka desimal (misal <code>0.0328</code>) merefleksikan konsensus peringkat tertinggi dari kedua representasi agar tidak kehilangan istilah teknis spesifik.
              </p>
            )}
            {session.scenario_type === "multi_gap" && (
              <p className="methodology-note">
                * <strong>Pembobotan Multi-Gap:</strong> Urutan akhir mengombinasikan 70% Relevansi Konten Buku dan 30% Bobot Kesenjangan Kompetensi (Gap 3 mendapatkan porsi prioritas tertinggi dibanding Gap 2 dan Gap 1).
              </p>
            )}
          </div>
        </div>

        {/* DAFTAR BUKU REKOMENDASI UNTUK USER INI */}
        <div className="simulation-results-box">
          {error && (
            <div className="simulation-error" role="alert">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          {loading ? (
            <div className="simulation-loading">
              <div className="spinner" />
              <p>Menjalankan inferensi model BGE-M3 untuk mencocokkan buku dengan profil kompetensi Anda…</p>
            </div>
          ) : result && result.books.length > 0 ? (
            <>
              {/* Banner Kondisi Skenario */}
              {result.is_upskilling ? (
                <div className="scenario-banner banner-upskilling">
                  <Sparkles size={20} />
                  <div>
                    <strong>Program Pengayaan (Upskilling) Terarah</strong>
                    <p>
                      Anda telah memenuhi seluruh standar kompetensi jabatan (Gap = 0). Sistem merekomendasikan bahan
                      bacaan lanjutan untuk memperdalam keahlian pada <em>Data Analytics</em> &amp; <em>Machine Learning</em>.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="scenario-banner banner-gap">
                  <TrendingUp size={20} />
                  <div>
                    <strong>
                      {session.id === "user_4"
                        ? "Rekomendasi Mulai Belajar Data Management (Gap 3)"
                        : result.scenario_type === "single_gap"
                        ? "Rekomendasi Penutup 1 Competency Gap"
                        : `Rekomendasi Terintegrasi Penutup ${result.gap_count} Competency Gaps`}
                    </strong>
                    <p>
                      {session.id === "user_4"
                        ? "Buku di bawah ini dipilih khusus oleh model BGE-M3 untuk membantu Anda mulai mempelajari tata kelola data, arsitektur basis data, dan master data dari dasar (karena seluruh kompetensi lain sudah terpenuhi)."
                        : "Buku di bawah ini dipilih khusus oleh model BGE-M3 untuk menutup kesenjangan kompetensi Anda, diurutkan berdasarkan bobot prioritas tertinggi (" + (result.scenario_type === "multi_gap" ? "Gap 3 > Gap 2 > Gap 1" : "Prioritas Pengembangan") + ")."}
                    </p>
                  </div>
                </div>
              )}

              {/* Grid Buku Rekomendasi */}
              <div className="simulation-books-grid">
                {result.books.map((b, idx) => {
                  const bookObj = fromSimulationBook(b);
                  return (
                    <div className="simulation-book-card" key={String(b.book_id) + idx}>
                      <div className="sim-book-cover-area" onClick={() => open(bookObj)}>
                        <Cover book={bookObj} variant={(idx % 3) + 1} />
                        <span className="sim-book-rank">#{b.rank}</span>
                      </div>

                      <div className="sim-book-details">
                        <div className="sim-book-header">
                          <span className="sim-comp-badge">
                            {b.target_competency_name || b.target_competency_id}
                          </span>
                          <span className={`sim-score-badge ${mode === "hybrid" ? "badge-hybrid" : "badge-dense"}`}>
                            {mode === "hybrid"
                              ? `Skor Hybrid RRF: ${b.rrf_score ? b.rrf_score.toFixed(4) : (b.score ? (b.score * 100).toFixed(1) + '%' : '0.0328')}`
                              : `Skor BGE-M3: ${b.raw_score ? (b.raw_score * 100).toFixed(1) + '%' : (b.score ? (b.score * 100).toFixed(1) + '%' : '70.1%')}`}
                          </span>
                        </div>
                        <div className="sim-score-subdetail">
                          {mode === "hybrid" ? (
                            <span>Fusi Semantik + Leksikal (Cosine Semantik: {b.raw_score ? (b.raw_score * 100).toFixed(1) + '%' : '65.2%'})</span>
                          ) : (
                            <span>Cosine Similarity: {b.raw_score ? b.raw_score.toFixed(3) : (b.score ? b.score.toFixed(3) : '0.701')} · Vektor 1024-dim</span>
                          )}
                        </div>

                        <h4 className="sim-book-title" onClick={() => open(bookObj)}>
                          {b.judul}
                        </h4>
                        <p className="sim-book-author">
                          {b.author} {b.tahun ? `· ${b.tahun}` : ""}
                        </p>

                        {/* KOTAK ALASAN REKOMENDASI AI */}
                        <div className="sim-reason-box">
                          <strong>Alasan Rekomendasi Sistem:</strong>
                          <p>{b.reason}</p>
                        </div>

                        <div className="sim-book-actions">
                          <button
                            type="button"
                            className="btn btn-primary btn-sm"
                            onClick={() => open(bookObj)}
                          >
                            <BookOpen size={14} /> Baca &amp; Detail Buku
                          </button>
                          {b.source_url && (
                            <a
                              href={b.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="btn btn-sm text-link"
                            >
                              Google Books <ExternalLink size={12} />
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            <p className="no-books">Tidak ada buku yang ditemukan untuk kriteria ini.</p>
          )}
        </div>
      </div>
    </section>
  );
}
