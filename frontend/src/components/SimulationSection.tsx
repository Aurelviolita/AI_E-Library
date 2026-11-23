import {
  AlertCircle,
  Award,
  BookOpen,
  Cpu,
  ExternalLink,
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
  session
}: {
  open: OpenBook;
  session: UserSession;
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
    session.scenario_type === "single_gap"
      ? "badge-amber"
      : session.scenario_type === "multi_gap"
      ? "badge-coral"
      : "badge-emerald";

  return (
    <section className="simulation-section" aria-label="Portal Rekomendasi Berbasis Competency Gap">
      {/* HEADER WORKSPACE KARYAWAN AKTIF (SESI LOGIN) */}
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
              Model Rekomendasi: <strong>BGE-M3 (1024-dim Semantik)</strong>
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
                      {result.scenario_type === "single_gap"
                        ? "Rekomendasi Penutup 1 Competency Gap"
                        : `Rekomendasi Terintegrasi Penutup ${result.gap_count} Competency Gaps`}
                    </strong>
                    <p>
                      Buku di bawah ini dipilih khusus oleh model BGE-M3 untuk menutup kesenjangan kompetensi Anda,
                      diurutkan berdasarkan bobot prioritas tertinggi (
                      {result.scenario_type === "multi_gap" ? "Gap 3 > Gap 2 > Gap 1" : "Prioritas Pengembangan"}).
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
                          <span className="sim-score-badge">
                            Skor BGE-M3: {b.personalized_score ? (b.personalized_score * 100).toFixed(0) : "85"}%
                          </span>
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
