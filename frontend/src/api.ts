import type { Book } from "./types";
import { catalogGroups, type CatalogGroup } from "./data/categories";

export type Competency = { competency_id: string; competency_name: string };

export type Health = {
  status: string;
  version: string;
  active_model: string;
  model_type: string;
  is_fallback: boolean;
  catalog_books_count: number;
  competencies_count: number;
  embedding_dimension?: number | null;
  catalog_exported_at?: string | null;
};

type CatalogBook = {
  book_id: string;
  judul: string;
  author: string;
  tahun: string | number;
  kategori_buku?: string;
  kategori?: string;
};

type ScoredBook = CatalogBook & { rank: number; score: number; model: string; is_fallback: boolean };

export type RecommendationsResult = { competency_name: string; competency_id: string; books: ScoredBook[] };
export type CatalogSort = "newest" | "oldest" | "title";
export const catalogPageSize = 4;

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(typeof body?.detail === "string" ? body.detail : "Layanan tidak dapat diakses. Coba lagi.");
  }
  return response.json();
}

function post<T>(endpoint: string, payload: object, signal?: AbortSignal) {
  return request<T>(`/api/v1/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
}

export function getCompetencies(signal?: AbortSignal) {
  return request<{ competencies: Competency[] }>("/api/v1/competencies", { signal });
}

export function getHealth(signal?: AbortSignal) {
  return request<Health>("/health", { signal, cache: "no-store" });
}

export function getRecommendations(competencyId: string, category: CatalogGroup | "", signal?: AbortSignal) {
  return post<RecommendationsResult>("recommend-books", {
    competency_id: competencyId,
    top_k: 20,
    categories: category ? catalogGroups[category] : undefined,
  }, signal);
}

export function mapBook(title: string, abstract: string, signal?: AbortSignal) {
  return post<{ query_title: string; recommendations: (Competency & { score: number; model: string; is_fallback: boolean })[] }>(
    "recommend-competencies",
    { title, abstract, top_k: 5 },
    signal,
  );
}

export function getBookDetail(id: string, signal: AbortSignal) {
  return request<{ book_id: string; abstrak: string; source_url?: string | null }>(`/api/v1/catalog/${encodeURIComponent(id)}`, { signal });
}

export function searchCatalog(term: string, category: CatalogGroup | "Semua", offset: number, sort: CatalogSort, signal: AbortSignal) {
  const params = new URLSearchParams({ q: term, limit: String(catalogPageSize), offset: String(offset), sort });
  if (category !== "Semua") {
    for (const value of catalogGroups[category]) params.append("category", value);
  }
  return request<{ books: CatalogBook[]; total_matched: number }>(`/api/v1/catalog?${params}`, { signal });
}

export function fromCatalog(book: CatalogBook): Book {
  return {
    id: book.book_id,
    title: book.judul,
    author: book.author,
    year: book.tahun,
    category: book.kategori_buku ?? book.kategori ?? "",
    tags: [],
  };
}

export function fromRecommendation(book: ScoredBook, competency: string): Book {
  return { ...fromCatalog(book), score: book.score, tags: [competency] };
}

export function findCompetency(competencies: Competency[], query: string) {
  const term = query.trim().toLowerCase();
  return competencies.find(({ competency_id, competency_name }) =>
    [competency_name, competency_id, `${competency_name} (${competency_id})`]
      .some((value) => value.toLowerCase() === term),
  );
}

export type BookAccess = { book_id: string; source_url: string | null; preview_url: string | null; web_reader_url: string | null; viewability: string; is_full_readable: boolean; verification: string };
export function getBookAccess(id: string, signal: AbortSignal) {
  return request<BookAccess>(`/api/v1/catalog/${encodeURIComponent(id)}/access`, { signal });
}

export type SimulationAssessment = {
  competency_id: string;
  competency_name: string;
  current_level: number;
  required_level: number;
  importance: number;
  gap: number;
  priority_label: string;
  notes?: string;
};

export type SimulationProfile = {
  id: string;
  name: string;
  current_role: string;
  target_role: string;
  scenario_type: "single_gap" | "multi_gap" | "zero_gap";
  scenario_badge: string;
  scenario_title: string;
  narrative: string;
  assessments: SimulationAssessment[];
  upskilling_tracks?: { competency_id: string; competency_name: string; topic: string }[];
};

export type SimulationBook = {
  book_id: string | number;
  judul: string;
  author: string;
  tahun?: string | number;
  kategori_buku?: string;
  kategori?: string;
  target_competency_id: string;
  target_competency_name: string;
  reason: string;
  personalized_score: number;
  score?: number;
  rank: number;
  model?: string;
  source_url?: string | null;
  google_id?: string | null;
  embed_url?: string | null;
  reader_url?: string | null;
};

export type SimulationResult = {
  status: string;
  profile: SimulationProfile;
  scenario_type: "single_gap" | "multi_gap" | "zero_gap";
  is_upskilling: boolean;
  gap_count: number;
  gaps: {
    competency_id: string;
    competency_name: string;
    current_level: number;
    required_level: number;
    gap: number;
    priority: number;
  }[];
  books: SimulationBook[];
  summary_note: string;
  retrieval_mode: "dense" | "hybrid";
};

export function getSimulationProfiles(signal?: AbortSignal) {
  return request<{ status: string; profiles: SimulationProfile[] }>("/api/v1/simulation/profiles", { signal });
}

export function getSimulationRecommendation(
  userId: string,
  mode: "dense" | "hybrid" = "dense",
  topK: number = 6,
  signal?: AbortSignal
) {
  return request<SimulationResult>(
    `/api/v1/simulation/recommend/${encodeURIComponent(userId)}?retrieval_mode=${mode}&top_k=${topK}`,
    { signal }
  );
}

export function fromSimulationBook(book: SimulationBook): Book {
  return {
    id: String(book.book_id),
    title: book.judul,
    author: book.author,
    year: book.tahun || "",
    score: book.personalized_score ?? book.score,
    tags: [book.target_competency_name || book.target_competency_id].filter(Boolean),
    category: book.kategori_buku || book.kategori || "",
  };
}

export type UserSession = {
  id: string;
  username: string;
  name: string;
  current_role: string;
  target_role: string;
  scenario_type: "single_gap" | "multi_gap" | "zero_gap";
  scenario_badge: string;
  session_token: string;
};

export function loginApi(username: string, password: string = "password", signal?: AbortSignal) {
  return post<{ status: string; session_token: string; user: Omit<UserSession, "session_token"> }>(
    "auth/login",
    { username, password },
    signal
  );
}
