const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let _token = null;

export function setToken(t) { _token = t; }
export function clearToken() { _token = null; }

async function request(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (_token) headers['Authorization'] = `Bearer ${_token}`;
  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const getProcesses = () => request('/processes');
export const getAnomalies = () => request('/anomalies');
export const login = (username, password) =>
  request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });
export const register = (username, password) =>
  request('/auth/register', { method: 'POST', body: JSON.stringify({ username, password }) });
export const postInvestigate = (anomalyId) =>
  request(`/investigations/${anomalyId}`, { method: 'POST' });
export const getInvestigation = (anomalyId) => request(`/investigations/${anomalyId}`);
export const clearAnomalies = () => request('/anomalies/clear', { method: 'DELETE' });
