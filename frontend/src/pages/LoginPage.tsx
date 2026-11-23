import { ArrowRight, BookOpen, Lock, User, Users } from "lucide-react";
import { useState } from "react";
import { loginApi, type UserSession } from "../api";

const PRESET_ACCOUNTS = [
  {
    username: "user1",
    id: "user_1",
    name: "User 1",
    role: "Junior Data Scientist",
    target: "Pratama Data Scientist",
    badge: "1 Competency Gap",
    badgeClass: "badge-amber",
    desc: "Target: Pratama Data Scientist. Kesenjangan pada Data Analytics (Gap = 1)."
  },
  {
    username: "user2",
    id: "user_2",
    name: "User 2",
    role: "Junior Data Analyst",
    target: "Pratama Data Scientist",
    badge: "3 Competency Gaps",
    badgeClass: "badge-coral",
    desc: "Target: Pratama Data Scientist. Kesenjangan: ML (Gap 3), Risk Mgmt (Gap 2), Data Analytics (Gap 1)."
  },
  {
    username: "user3",
    id: "user_3",
    name: "User 3",
    role: "Pratama Data Scientist",
    target: "Pengembangan Lanjutan",
    badge: "0 Gap · Upskilling",
    badgeClass: "badge-emerald",
    desc: "Semua standar kompetensi terpenuhi (Gap = 0). Rekomendasi upskilling materi lanjutan."
  }
];

export function LoginPage({ onLogin }: { onLogin: (session: UserSession) => void }) {
  const [username, setUsername] = useState("user1");
  const [password, setPassword] = useState("password");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLogin(e?: React.FormEvent, customUser?: string) {
    if (e) e.preventDefault();
    const targetUser = customUser || username;
    setLoading(true);
    setError(null);
    try {
      const res = await loginApi(targetUser, password);
      const sessionData: UserSession = {
        ...res.user,
        session_token: res.session_token
      };
      localStorage.setItem("bpjs_elibrary_session", JSON.stringify(sessionData));
      onLogin(sessionData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal masuk. Periksa username dan password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-shell">
        {/* BRAND & HEADER */}
        <div className="login-brand">
          <div className="login-brand-icon">
            <BookOpen size={28} />
          </div>
          <h1>e-Library</h1>
          <span className="login-subbrand">BPJS KESEHATAN · PORTAL KOMPETENSI</span>
          <p className="login-tagline">
            Sistem rekomendasi buku berbasis kesenjangan kompetensi (<em>Competency Gap</em>) untuk pengembangan karier karyawan.
          </p>
        </div>

        {/* LOGIN FORM CARD */}
        <div className="login-card">
          <div className="login-card-header">
            <span className="eyebrow">AUTENTIKASI SESI PENGGUNA</span>
            <h2>Masuk ke Akun Karyawan</h2>
            <p>Silakan masuk menggunakan akun karyawan untuk melihat rencana karier dan rekomendasi buku yang dipersonalisasi.</p>
          </div>

          <form className="login-form" onSubmit={(e) => handleLogin(e)}>
            <div className="form-group">
              <label htmlFor="login-username">
                <User size={15} /> Username
              </label>
              <input
                id="login-username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="user1, user2, atau user3"
              />
            </div>

            <div className="form-group">
              <label htmlFor="login-password">
                <Lock size={15} /> Password
              </label>
              <input
                id="login-password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="password"
              />
            </div>

            {error && <div className="login-error" role="alert">{error}</div>}

            <button type="submit" className="btn btn-gold login-submit-btn" disabled={loading}>
              {loading ? "Memproses..." : "Masuk ke Portal"} <ArrowRight size={18} />
            </button>
          </form>

          {/* 1-CLICK DEMO ACCOUNTS PRESET */}
          <div className="demo-accounts-divider">
            <span>ATAU PILIH AKUN LANGSUNG UNTUK SIMULASI</span>
          </div>

          <div className="demo-accounts-list">
            {PRESET_ACCOUNTS.map((acc) => (
              <button
                key={acc.username}
                type="button"
                className="demo-account-item"
                onClick={() => handleLogin(undefined, acc.username)}
                disabled={loading}
              >
                <div className="demo-acc-top">
                  <div className="demo-acc-user">
                    <div className="demo-acc-avatar">
                      {acc.username === "user2" ? <Users size={16} /> : <User size={16} />}
                    </div>
                    <div>
                      <strong>{acc.name}</strong>
                      <span className="demo-acc-sub">{acc.role} ➔ {acc.target}</span>
                    </div>
                  </div>
                  <span className={`simulation-badge ${acc.badgeClass}`}>{acc.badge}</span>
                </div>
                <p className="demo-acc-desc">{acc.desc}</p>
                <span className="demo-acc-action">Klik untuk masuk sebagai {acc.name} ➔</span>
              </button>
            ))}
          </div>
        </div>

        <div className="login-footer">
          <span>e-Library BPJS Kesehatan · Rekomendasi NLP Cerdas BGE-M3</span>
        </div>
      </div>
    </div>
  );
}
