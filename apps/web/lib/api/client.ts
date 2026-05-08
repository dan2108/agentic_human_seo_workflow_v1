const API_URL =
  typeof window === "undefined"
    ? (process.env.API_URL ?? "http://localhost:8000")
    : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000");

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  jobs: {
    create: (data: unknown) => apiFetch<{ id: string; site_url: string; status: string; created_at: string }>("/jobs/", { method: "POST", body: JSON.stringify(data) }),
    get: (id: string) => apiFetch<{ id: string; site_url: string; status: string; created_at: string }>(`/jobs/${id}`),
    list: () => apiFetch<Array<{ id: string; site_url: string; status: string; created_at: string }>>("/jobs/"),
  },
  gates: {
    get: (id: string) => apiFetch<{ id: string; gate_id: string; status: string; decision: string | null; comment: string | null; synthesis: Record<string, unknown> }>(`/gates/${id}`),
    approve: (id: string, comment?: string) =>
      apiFetch<{ status: string }>(`/gates/${id}/approve`, { method: "POST", body: JSON.stringify({ comment }) }),
    reject: (id: string, comment?: string) =>
      apiFetch<{ status: string }>(`/gates/${id}/reject`, { method: "POST", body: JSON.stringify({ comment }) }),
  },
  content: {
    getDraft: (id: string) => apiFetch<Record<string, unknown>>(`/content/${id}`),
    saveDraft: (id: string, body: string) =>
      apiFetch<Record<string, unknown>>(`/content/${id}`, { method: "PATCH", body: JSON.stringify({ body }) }),
  },
  aftercare: {
    getReports: (jobId: string) => apiFetch<unknown[]>(`/aftercare/${jobId}`),
  },
};
