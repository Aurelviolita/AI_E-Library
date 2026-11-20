import { useState } from "react";
import type { Competency } from "../api";

interface Assessment { competency_id: string; current_level: number; required_level: number; importance: number }
interface Gap { competency_id: string; competency_name: string; gap: number; priority: number }
interface SuggestedBook { source_url?: string | null; book_id: string; judul: string; author: string; target_competency_id: string; reason: string; personalized_score: number; model: string }
interface Plan { gap_count: number; gaps: Gap[]; books: SuggestedBook[]; disclaimer: string }

export function GapPlanner({ competencies }: { competencies: Competency[] }) {
  const [rows, setRows] = useState<Assessment[]>([{ competency_id: "", current_level: 2, required_level: 4, importance: 3 }]);
  const [assessmentSource, setAssessmentSource] = useState<"simulasi" | "hasil_asesmen_resmi">("simulasi");
  const [mode, setMode] = useState<"dense" | "hybrid">("hybrid");
  const [result, setResult] = useState<Plan | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function update(index: number, changes: Partial<Assessment>) {
    setRows(old => old.map((r, i) => i === index ? { ...r, ...changes } : r));
    setResult(null);
  }
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setError(""); setResult(null);
    try {
      const response = await fetch("/api/v1/personalized-learning", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assessment_source: assessmentSource, assessments: rows, scale_max: 5, top_k: 8, retrieval_mode: mode }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "Gagal memproses asesmen");
      setResult(payload as Plan);
    } catch (e) { setError(e instanceof Error ? e.message : "Tidak dapat tersambung ke API"); }
    finally { setBusy(false); }
  }
  return (
    <section className="paper gap-planner" aria-label="Rencana pembelajaran berdasarkan asesmen">
      <div className="panel-top"><span className="step-label">PERSONALISASI / BERDASARKAN ASESMEN</span></div>
      <h2>Rencana Belajar Sesuai Competency Gap</h2>
      <p>Isi nilai berdasarkan hasil asesmen resmi jika tersedia, atau gunakan simulasi untuk mencoba sistem. Skala 0–5 di sini adalah contoh, bukan standar asesmen resmi BPJS. Data yang dimasukkan tidak disimpan oleh fitur ini.</p>
      <div className="assessment-guide">
        <h3>Nilai asesmen ini asalnya dari mana?</h3>
        <p>Untuk penggunaan nyata, nilai aktual berasal dari asesmen kompetensi yang dilakukan organisasi (misalnya evaluasi atasan, asesmen berbasis indikator perilaku, atau hasil penilaian yang disahkan HR). Target kompetensi harus berasal dari standar jabatan yang berlaku. Sistem ini belum terhubung ke database asesmen internal.</p>
        <label>Sumber nilai
          <select value={assessmentSource} onChange={e => { setAssessmentSource(e.target.value as "simulasi" | "hasil_asesmen_resmi"); setResult(null); }}>
            <option value="simulasi">Simulasi / latihan (bukan asesmen resmi)</option>
            <option value="hasil_asesmen_resmi">Input manual dari hasil asesmen resmi</option>
          </select>
        </label>
        <details>
          <summary>Panduan skala contoh 0–5 (klik untuk lihat)</summary>
          <p><strong>0</strong> belum pernah menerapkan; <strong>1</strong> mengenali dasar; <strong>2</strong> mampu dengan bimbingan; <strong>3</strong> mandiri pada tugas rutin; <strong>4</strong> mampu menangani kasus kompleks; <strong>5</strong> mampu membimbing orang lain. Ini hanya rubrik ilustrasi dan perlu disesuaikan dengan indikator resmi per kompetensi.</p>
          <p>Contoh simulasi: nilai sekarang 2, target 4 berarti gap 2. Bobot 1–5 menunjukkan prioritas kebutuhan belajar, bukan nilai kemampuan. Jangan gunakan angka simulasi untuk keputusan kepegawaian.</p>
        </details>
        {assessmentSource === "hasil_asesmen_resmi" && <p className="access-note">Pastikan skor dan target sudah dinormalisasi ke skala 0–5 dengan metode yang disetujui pengelola kompetensi. Jangan memasukkan data personal karyawan.</p>}
      </div>
      <form onSubmit={submit}>
        {rows.map((row, idx) => (
          <div className="gap-planner-row" key={idx}>
            <label>Kompetensi
              <select required value={row.competency_id} onChange={e => update(idx, { competency_id: e.target.value })}>
                <option value="">Pilih kompetensi</option>
                {competencies.map(c => <option key={c.competency_id} value={c.competency_id}>{c.competency_id} · {c.competency_name}</option>)}
              </select>
            </label>
            <label>Nilai aktual (0–5)
              <input type="number" min="0" max="5" step="0.5" required value={row.current_level} onChange={e => update(idx, { current_level: Number(e.target.value) })} />
            </label>
            <label>Target jabatan (0–5)
              <input type="number" min="0" max="5" step="0.5" required value={row.required_level} onChange={e => update(idx, { required_level: Number(e.target.value) })} />
            </label>
            <label>Prioritas (1–5)
              <input type="number" min="1" max="5" required value={row.importance} onChange={e => update(idx, { importance: Number(e.target.value) })} />
            </label>
            <button type="button" className="btn" disabled={rows.length === 1} onClick={() => setRows(old => old.filter((_, i) => i !== idx))}>Hapus</button>
          </div>
        ))}
        <div className="gap-planner-actions">
          <button type="button" className="btn" disabled={rows.length >= 67} onClick={() => setRows(old => [...old, { competency_id: "", current_level: 2, required_level: 4, importance: 3 }])}>+ Tambah kompetensi</button>
          <label>Metode pencarian <select value={mode} onChange={e => setMode(e.target.value as "dense" | "hybrid")}><option value="hybrid">BGE-M3 + TF-IDF (hybrid)</option><option value="dense">BGE-M3 (semantik)</option></select></label>
          <button type="submit" className="btn btn-primary" disabled={busy || competencies.length === 0}>{busy ? "Menghitung…" : "Buat rencana belajar"}</button>
        </div>
      </form>
      {error && <p className="field-error" role="alert">{error}</p>}
      {result && <div className="gap-results" aria-live="polite">
        <h3>{result.gap_count ? `${result.gap_count} kesenjangan teridentifikasi` : "Tidak ada kesenjangan pada nilai yang dimasukkan"}</h3>
        {result.gaps.map(g => <p key={g.competency_id}><strong>{g.competency_name}:</strong> selisih {g.gap.toFixed(1)}, prioritas {g.priority.toFixed(2)}</p>)}
        {result.books.length > 0 && <h3>Buku yang disarankan</h3>}
        {result.books.map((b, i) => <article className="gap-book" key={b.book_id}>
          <strong>{i + 1}. {b.judul}</strong><span>{b.author} · {b.target_competency_id}</span>
          <p>{b.reason}</p>{b.source_url && <a href={b.source_url} target="_blank" rel="noopener noreferrer">Lihat buku di Google Books ↗</a>}<small>Mesin: {b.model}; skor pengurutan relatif {b.personalized_score.toFixed(3)}</small>
        </article>)}
        <p className="gap-disclaimer">{result.disclaimer}</p>
      </div>}
    </section>
  );
}
