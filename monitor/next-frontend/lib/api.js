export async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(`/api${path}`, {
      ...options,
      credentials: "same-origin",
      cache: "no-store",
      headers: { "Content-Type": "application/json", ...options.headers },
    });
  } catch {
    throw new Error("API 서버에 연결하지 못했습니다.");
  }
  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(data?.message || `요청이 실패했습니다. (${response.status})`);
    error.status = response.status;
    throw error;
  }
  return data;
}

export const getMe = () => api("/auth/me");
export const login = (username, password) => api("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) });
export const logout = () => api("/auth/logout", { method: "POST" });
export const listNotes = () => api("/notes");
export const listEvents = () => api("/events");
export const getNote = id => api(`/notes/${id}`);
export const createNote = values => api("/notes", { method: "POST", body: JSON.stringify(values) });
export const updateNote = (id, values) => api(`/notes/${id}`, { method: "PUT", body: JSON.stringify(values) });
export const deleteNote = id => api(`/notes/${id}`, { method: "DELETE" });
export const startObservation = () => api("/analysis/start", { method: "POST" });
export const getAnalysis = (afterId, threshold, referenceTime) => {
  const query = new URLSearchParams({ after_id: String(afterId), threshold: String(threshold) });
  if (referenceTime) query.set("reference_time", referenceTime);
  return api(`/analysis?${query}`);
};
