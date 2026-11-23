import { ArrowRight, ChevronRight, LogOut, Menu, Search, User } from "lucide-react";
import { useState, type Ref } from "react";
import { nav } from "../data/navigation";
import type { Page } from "../types";
import type { UserSession } from "../api";

export function Topbar({
  page,
  menuButton,
  onMenu,
  onSearch,
  session,
  onLogout
}: {
  page: Page;
  menuButton: Ref<HTMLButtonElement>;
  onMenu: () => void;
  onSearch: (query: string) => void;
  session: UserSession;
  onLogout: () => void;
}) {
  const [query, setQuery] = useState("");

  return (
    <header className="topbar">
      <button ref={menuButton} className="mobile-menu icon-button" onClick={onMenu} aria-label="Buka menu navigasi">
        <Menu size={22} />
      </button>

      <div className="breadcrumb">
        <span>Perpustakaan</span>
        <ChevronRight size={13} />
        <strong>{nav.find((item) => item.id === page)?.label}</strong>
      </div>

      <form
        className="global-search"
        role="search"
        onSubmit={(event) => {
          event.preventDefault();
          onSearch(query.trim());
        }}
      >
        <Search size={16} />
        <input
          aria-label="Cari buku, penulis, atau kode kompetensi"
          placeholder="Cari buku atau penulis…"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button aria-label="Cari di katalog"><ArrowRight size={16} /></button>
      </form>

      {/* USER PROFILE INFO & LOGOUT BUTTON */}
      <div className="topbar-session-area">
        <div className="topbar-session-badge">
          <div className="topbar-user-avatar">
            <User size={15} />
          </div>
          <div className="topbar-user-info">
            <span className="topbar-user-name">{session.name}</span>
            <span className="topbar-user-role">{session.current_role}</span>
          </div>
        </div>

        <button
          type="button"
          className="topbar-logout-btn"
          onClick={onLogout}
          title="Keluar dari sesi akun karyawan"
        >
          <LogOut size={14} />
          <span>Keluar</span>
        </button>
      </div>
    </header>
  );
}
