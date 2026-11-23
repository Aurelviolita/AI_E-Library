import { BookOpenText, ChevronDown, ExternalLink, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { getBookAccess, getBookDetail, type BookAccess } from "../api";
import { similarityDescription, similarityFormat } from "../data/similarity";
import type { Book } from "../types";
import { Cover } from "./Cover";

export function BookModal({ book, onClose: close }: { book: Book; onClose: () => void }) {
  const { score } = book;
  const [abstract, setAbstract] = useState<string | null>(null);
  const [access, setAccess] = useState<BookAccess | null>(null);
  const [sourceUrl, setSourceUrl] = useState<string | null>(null);
  const [failure, setFailure] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    getBookDetail(book.id, controller.signal)
      .then((data) => { if (!controller.signal.aborted) setAbstract(data.abstrak); setSourceUrl(data.source_url ?? null); })
      .catch(() => { if (!controller.signal.aborted) setFailure(true); });
    getBookAccess(book.id, controller.signal)
      .then(data => { if (!controller.signal.aborted) setAccess(data); })
      .catch(() => { /* Metadata eksternal boleh tidak tersedia; link katalog tetap muncul. */ });
    return () => controller.abort();
  }, [book.id, attempt]);
  const dialog = useRef<HTMLDialogElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);
  const [expanded, setExpanded] = useState(false);
  const [showInlineReader, setShowInlineReader] = useState(false);

  const effectiveUrl = access?.source_url || sourceUrl;
  let googleId: string | null = null;
  if (effectiveUrl) {
    try {
      const u = new URL(effectiveUrl);
      googleId = u.searchParams.get("id");
    } catch {
      const m = effectiveUrl.match(/[?&]id=([^&]+)/);
      if (m) googleId = m[1];
    }
  }
  const embedUrl = googleId ? `https://books.google.com/books?id=${googleId}&printsec=frontcover&output=embed` : null;
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const element = dialog.current;
    element?.showModal();
    closeButton.current?.focus();
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      element?.close();
      document.body.style.overflow = overflow;
      previous?.focus();
    };
  }, []);
  return (
    <dialog
      ref={dialog}
      className="book-dialog"
      aria-labelledby="detail-title"
      onCancel={(e) => {
        e.preventDefault();
        close();
      }}
      onClick={(e) => {
        if (e.target === dialog.current) close();
      }}
    >
      <div className="detail-shell">
        <button
          ref={closeButton}
          className="detail-close icon-button"
          onClick={close}
          aria-label="Tutup detail buku"
        >
          <X size={21} />
        </button>
        <div className="detail-art">
          <Cover book={book} />
          <p>SAMPUL RESMI JIKA TERSEDIA · ILUSTRASI JIKA TIDAK</p>
        </div>
        <div className="detail-content">
          <div className="detail-kicker">
            <span className="book-category">{book.category}</span>
          </div>
          <h2 id="detail-title">{book.title}</h2>
          <p className="detail-author">
            {book.author}
            <span>·</span>
            {book.year}
          </p>
          {score !== undefined && (
            <div className="similarity">
              <div>
                <span>Skor kemiripan</span>
                <strong>{similarityFormat.format(score)}</strong>
              </div>
              <p>{similarityDescription}</p>
            </div>
          )}
          <section>
            <h3>Tentang buku</h3>
            {failure ? (
              <p role="alert">
                Ringkasan gagal dimuat.{" "}
                <button className="text-link" onClick={() => { setFailure(false); setAttempt((n) => n + 1); }}>
                  Coba lagi
                </button>
              </p>
            ) : abstract === null ? (
              <p role="status">Memuat ringkasan…</p>
            ) : (
              <p className="line-clamp-3">{abstract || "Ringkasan belum tersedia."}</p>
            )}
          </section>
          <section className="book-access">
            <h3>Akses buku</h3>
            <p>Akses baca mengikuti ketentuan Google Books. Tidak semua buku menyediakan pratinjau atau bacaan lengkap.</p>
            <div className="access-buttons">
              {embedUrl && (
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => setShowInlineReader(!showInlineReader)}
                >
                  <BookOpenText size={16} />
                  {showInlineReader ? "Tutup Bacaan Langsung" : "Baca Buku Langsung"}
                </button>
              )}
              {access?.web_reader_url && <a className="btn" href={access.web_reader_url} target="_blank" rel="noopener noreferrer"><BookOpenText size={16}/> {access.is_full_readable ? "Buka Tab Bacaan" : "Buka Pratinjau"} <ExternalLink size={14}/></a>}
              {!access?.web_reader_url && access?.preview_url && <a className="btn" href={access.preview_url} target="_blank" rel="noopener noreferrer"><BookOpenText size={16}/> Preview Tab <ExternalLink size={14}/></a>}
              {effectiveUrl && <a className="btn" href={effectiveUrl} target="_blank" rel="noopener noreferrer">Google Books <ExternalLink size={14}/></a>}
            </div>
            {showInlineReader && embedUrl && (
              <div style={{ marginTop: '16px', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--line)', background: '#fff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: '#f0ede4', borderBottom: '1px solid var(--line)', fontSize: '12px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--ink)' }}>Pratinjau Pembaca Buku Langsung (Google Books)</span>
                  <button type="button" className="text-link" style={{ fontSize: '12px' }} onClick={() => setShowInlineReader(false)}>Sembunyikan</button>
                </div>
                <iframe
                  src={embedUrl}
                  title={`Baca ${book.title}`}
                  width="100%"
                  height="460px"
                  style={{ border: 'none', display: 'block' }}
                  allowFullScreen
                />
              </div>
            )}
            {access?.verification === "google_books_api" && <p className="access-note">Status akses: {access.is_full_readable ? "Bacaan penuh tersedia" : access.viewability === "PARTIAL" ? "Pratinjau terbatas" : "Tidak ada pratinjau yang dikonfirmasi"}.</p>}
            {access?.verification === "metadata_unavailable" && <p className="access-note">Status pratinjau belum bisa dicek. Coba buka halaman Google Books.</p>}
            {!sourceUrl && !access?.source_url && <p className="unavailable">Tautan buku belum tersedia.</p>}
          </section>
          <section>
            <h3>Kompetensi terkait</h3>
            {book.tags.length ? (
              <div className="competency-tags">
                {book.tags.map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>
            ) : (
              <p className="unavailable">Belum tersedia di katalog</p>
            )}
          </section>
          {abstract && <button
            className="summary-toggle"
            onClick={() => setExpanded(!expanded)}
            aria-expanded={expanded}
            aria-controls="book-summary"
          >
            <BookOpenText size={18} />
            {expanded ? "Tutup ringkasan buku" : "Baca ringkasan buku"}
            <ChevronDown size={17} className={expanded ? "rotated" : ""} />
          </button>}
          {expanded && abstract && (
            <div id="book-summary" className="book-summary">
              {abstract.split(/\n\s*\n/).map((paragraph, i) => (
                <p key={i}>{paragraph}</p>
              ))}
            </div>
          )}
        </div>
      </div>
    </dialog>
  );
}
