const BASE_URL = "http://localhost:8000";

export async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (response.status === 401) {
    localStorage.removeItem("token");
    window.location.replace("/login");
    throw new Error("Session expired. Please log in again.");
  }

  if (response.status === 204) return null;

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong");
  }

  return data;
}
