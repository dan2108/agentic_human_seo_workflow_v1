// FastAPI client - typed wrapper for all API calls
const API_URL = process.env.API_URL ?? "http://localhost:8000";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

// Jobs
export const api = {
  jobs: {
    create: (data: unknown) => apiFetch("/jobs", { method: "POST", body: JSON.stringify(data) }),
    get: (id: string) => apiFetch(`/jobs/${id}`),
    list: () => apiFetch("/jobs"),
  },
  gates: {
    get: (id: string) => apiFetch(`/gates/${id}`),
    approve: (id: string, comment?: string) =>
      apiFetch(`/gates/${id}/approve`, { method: "POST", body: JSON.stringify({ comment }) }),
    reject: (id: string, comment: string) =>
      apiFetch(`/gates/${id}/reject`, { method: "POST", body: JSON.stringify({ comment }) }),
  },
  content: {
    getDraft: (id: string) => apiFetch(`/content/${id}`),
    saveDraft: (id: string, body: string) =>
      apiFetch(`/content/${id}`, { method: "PATCH", body: JSON.stringify({ body }) }),
  },
  aftercare: {
    getReports: (jobId: string) => apiFetch(`/aftercare/${jobId}`),
  },
};
