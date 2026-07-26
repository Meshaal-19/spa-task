import { request } from "./client";

export function getNotes() {
  return request("/notes/");
}

export function createNote(title, body) {
  return request("/notes/", {
    method: "POST",
    body: JSON.stringify({ title, body }),
  });
}

export function updateNote(id, title, body) {
  return request(`/notes/${id}`, {
    method: "PUT",
    body: JSON.stringify({ title, body }),
  });
}

export function deleteNote(id) {
  return request(`/notes/${id}`, { method: "DELETE" });
}
