import os


def read_file(path: str) -> str:
    MAX_CHARS = 3000
    if not os.path.exists(path):
        return f"Error: File not found: {path}"
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            parts = [page.extract_text() or "" for page in reader.pages]
            content = "\n".join(parts)
        except ImportError:
            return "Error: pypdf not installed. Run: pip install pypdf"
        except Exception as e:
            return f"Error reading PDF: {e}"
    else:
        return f"Error: Unsupported file type '{ext}'. Only .txt and .pdf are supported."
    if len(content) > MAX_CHARS:
        content = content[:MAX_CHARS] + "\n...[truncated]"
    return content
