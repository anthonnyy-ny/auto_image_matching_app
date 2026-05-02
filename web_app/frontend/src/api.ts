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

export function uploadImages(projectId: string, files: FileList) {
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

export function imageUrl(projectId: string, sourcePath: string) {
  return `${API_BASE}/api/projects/${projectId}/image?path=${encodeURIComponent(sourcePath)}`;
}
