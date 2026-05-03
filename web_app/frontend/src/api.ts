export const API_BASE = "http://127.0.0.1:8000";

export type Project = {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  image_count: number;
};

export type ResultImage = {
  filename: string;
  source_path: string;
};

export type ResultGroup = {
  name: string;
  count: number;
  images: ResultImage[];
};

export type MatchResponse = {
  project_id: string;
  group_count: number;
  elapsed: number;
  stats: Record<string, unknown>;
  groups: ResultGroup[];
};

export type JobState = {
  id: string;
  project_id: string;
  status: "running" | "done" | "failed" | "cancelled";
  progress: number;
  message: string;
  metrics?: Record<string, unknown>;
  result?: MatchResponse;
  error?: string;
};

export type AiStatus = {
  ai_backend: string;
  ai_model: string;
  ai_model_source?: string;
  ai_status?: string;
  ai_ready?: boolean;
  ai_device?: string;
  ai_framework?: string;
  ai_allow_download?: boolean;
  ai_last_error?: string | null;
  embedding_dim?: number;
  ai_cache_hits?: number;
  ai_cache_misses?: number;
  ai_cache_writes?: number;
  available_models?: { id: string; source: string; recommended?: boolean }[];
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function createProject(name: string) {
  return request<Project>("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export function listProjects() {
  return request<Project[]>("/api/projects");
}

export function getProject(projectId: string) {
  return request<Project>(`/api/projects/${projectId}`);
}

export function uploadImages(projectId: string, files: FileList | File[]) {
  const form = new FormData();
  Array.from(files).forEach((file) => form.append("files", file));
  return request<{ uploaded: number; image_count: number }>(`/api/projects/${projectId}/images`, {
    method: "POST",
    body: form,
  });
}

export function matchProject(projectId: string, mode = "fast") {
  return request<MatchResponse>(`/api/projects/${projectId}/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode }),
  });
}

export function startMatchJob(projectId: string, mode = "fast") {
  return request<{ job_id: string; status: string }>(`/api/projects/${projectId}/match/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode }),
  });
}

export function getJob(jobId: string) {
  return request<JobState>(`/api/jobs/${jobId}`);
}

export function cancelJob(jobId: string) {
  return request<JobState>(`/api/jobs/${jobId}/cancel`, { method: "POST" });
}

export function clearCache() {
  return request<{ removed_files: number; removed_bytes: number }>("/api/cache/clear", { method: "POST" });
}

export function getAiStatus() {
  return request<AiStatus>("/api/ai/status");
}

export function reloadAi() {
  return request<AiStatus>("/api/ai/reload", { method: "POST" });
}

export function getResults(projectId: string) {
  return request<{ project_id: string; groups: ResultGroup[]; stats: Record<string, unknown> }>(`/api/projects/${projectId}/results`);
}

export function updateResults(projectId: string, groups: ResultGroup[]) {
  return request<{ project_id: string; groups: ResultGroup[] }>(`/api/projects/${projectId}/results`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ groups }),
  });
}

export function importProject(file: File) {
  const form = new FormData();
  form.append("file", file);
  return request<Project>("/api/projects/import", {
    method: "POST",
    body: form,
  });
}

export function exportUrl(projectId: string) {
  return `${API_BASE}/api/projects/${projectId}/export`;
}

export function projectFileUrl(projectId: string) {
  return `${API_BASE}/api/projects/${projectId}/project-file`;
}

export function imageUrl(projectId: string, sourcePath: string) {
  return `${API_BASE}/api/projects/${projectId}/image?path=${encodeURIComponent(sourcePath)}`;
}
