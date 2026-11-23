import { ArrowRight, ArrowUpRight, BookOpen, CircleHelp, Compass, FileSearch, Library } from "lucide-react";
import { useEffect, useState } from "react";
import type { Book, OpenBook, Page } from "../types";
import { fromCatalog, searchCatalog, type Health, type UserSession } from "../api";
import { BookCard } from "../components/BookCard";
import { Empty, Skeleton } from "../components/LibraryStates";
import { SimulationSection } from "../components/SimulationSection";

export function Dashboard({
  go,
  open,
  health,
  session
}: {
  go: (p: Page) => void;
  open: OpenBook;
  health: Health | null;
  session: UserSession;
}) {
  const [books, setBooks] = useState<Book[] | null>(null);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    searchCatalog("", "Semua", 0, "newest", controller.signal)
      .then((result) => { if (!controller.signal.aborted) setBooks(result.books.map(fromCatalog)); })
      .catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [attempt]);

  return (
    <>
      <div className="dashboard-intro">
        <span className="eyebrow">PORTAL PENGEMBANGAN KARYAWAN &amp; E-LIBRARY</span>
      </div>

      {/* HASIL ASESMEN STANDAR KOMPETENSI & REKOMENDASI AI DI BAGIAN ATAS */}
      <SimulationSection open={open} session={session} />

      {/* SUDUT BACA PILIHAN DARI KATALOG */}
      <section className="curated">
        <div className="section-heading">
          <div>
            <div className="eyebrow">DARI RAK PERPUSTAKAAN</div>
            <h2>Sudut baca pilihan</h2>
            <p>Tambahan terbaru dari katalog perpustakaan.</p>
          </div>
          <button className="text-link" onClick={() => go("catalog")}>
            Lihat katalog <ArrowRight size={17} />
          </button>
        </div>
        {error ? (
          <Empty title="Koleksi belum dapat dimuat" action={<button className="text-link" onClick={() => { setError(false); setAttempt((n) => n + 1); }}>Coba lagi</button>}>
            Muat ulang koleksi dari katalog.
          </Empty>
        ) : books === null ? <Skeleton count={4} /> : books.length === 0 ? (
          <Empty title="Katalog masih kosong">Buku terbaru akan muncul di sini.</Empty>
        ) : (
          <div className="book-grid dashboard-grid">
            {books.map((book) => <BookCard key={book.id} book={book} open={open} />)}
          </div>
        )}
      </section>

      {/* RINGKASAN KOLEKSI PERPUSTAKAAN & NAVIGASI CEPAT */}
      <section className="overview" aria-label="Jelajahi perpustakaan">
        <div className="overview-stat">
          <Library size={23} strokeWidth={1.4} />
          <div>
            <strong>
              {health?.catalog_books_count.toLocaleString("id-ID") ?? "–"}<span> buku</span>
            </strong>
            <p>Total katalog</p>
          </div>
        </div>
        <div className="overview-stat">
          <Compass size={25} strokeWidth={1.4} />
          <div>
            <strong>
              {health?.competencies_count.toLocaleString("id-ID") ?? "–"}<span> kompetensi</span>
            </strong>
            <p>Arah pengembangan Anda</p>
          </div>
        </div>
        <button className="overview-link" onClick={() => go("mapping")}>
          <FileSearch size={21} strokeWidth={1.5} />
          <div>
            <strong>Petakan buku baru</strong>
            <p>Temukan kompetensi terkait</p>
          </div>
          <ArrowUpRight size={18} />
        </button>
        <button className="overview-link" onClick={() => go("catalog")}>
          <BookOpen size={22} strokeWidth={1.5} />
          <div>
            <strong>Buka katalog</strong>
            <p>Jelajahi koleksi buku</p>
          </div>
          <ArrowUpRight size={18} />
        </button>
      </section>

      <div className="library-note">
        <CircleHelp size={15} />
        <p>
          Sampul buku pada halaman ini merupakan ilustrasi katalog.
        </p>
      </div>
    </>
  );
}
