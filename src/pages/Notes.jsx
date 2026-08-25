import { useState, useEffect } from "react";
import { getNotes, createNote, updateNote, deleteNote } from "../api/notes";

export default function Notes() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newBody, setNewBody] = useState("");
  const [creating, setCreating] = useState(false);

  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [editBody, setEditBody] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await getNotes();
        if (!cancelled) setNotes(data);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setError("");
    setCreating(true);
    try {
      const note = await createNote(newTitle.trim(), newBody.trim());
      setNotes((prev) => [note, ...prev]);
      setNewTitle("");
      setNewBody("");
      setShowCreate(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  }

  function startEdit(note) {
    setEditingId(note.id);
    setEditTitle(note.title);
    setEditBody(note.body);
  }

  function cancelEdit() {
    setEditingId(null);
    setEditTitle("");
    setEditBody("");
  }

  async function handleUpdate(e, noteId) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const updated = await updateNote(noteId, editTitle.trim(), editBody.trim());
      setNotes((prev) => prev.map((n) => (n.id === noteId ? updated : n)));
      cancelEdit();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(noteId) {
    setError("");
    try {
      await deleteNote(noteId);
      setNotes((prev) => prev.filter((n) => n.id !== noteId));
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <div className="notes-loading">Loading notes…</div>;

  return (
    <div>
      <div className="notes-header">
        <h1>My Notes</h1>
        <button
          className="btn btn-primary"
          onClick={() => {
            setShowCreate((v) => !v);
            setError("");
          }}
        >
          {showCreate ? "Cancel" : "+ New Note"}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {showCreate && (
        <form className="note-form" onSubmit={handleCreate}>
          <input
            type="text"
            placeholder="Title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            required
          />
          <textarea
            placeholder="Body (optional)"
            value={newBody}
            onChange={(e) => setNewBody(e.target.value)}
          />
          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={creating}>
              {creating ? "Saving…" : "Save Note"}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setShowCreate(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {notes.length === 0 && !showCreate && (
        <div className="notes-empty">
          No notes yet. Hit &ldquo;+ New Note&rdquo; to create your first one.
        </div>
      )}

      <div className="notes-grid">
        {notes.map((note) =>
          editingId === note.id ? (
            <form
              key={note.id}
              className="note-card note-edit-form"
              onSubmit={(e) => handleUpdate(e, note.id)}
            >
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                required
              />
              <textarea
                value={editBody}
                onChange={(e) => setEditBody(e.target.value)}
              />
              <div className="note-actions">
                <button
                  type="submit"
                  className="btn btn-primary btn-sm"
                  disabled={saving}
                >
                  {saving ? "Saving…" : "Save"}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={cancelEdit}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div key={note.id} className="note-card">
              <div className="note-card-title">{note.title}</div>
              {note.body && <div className="note-card-body">{note.body}</div>}
              <div className="note-actions">
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => startEdit(note)}
                >
                  Edit
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => handleDelete(note.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}
