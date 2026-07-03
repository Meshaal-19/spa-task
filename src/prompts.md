# AI Prompt Log

## 23 June 2026

### Task: Build a React SPA with 3 routes and shared layout

Prompt:
Explain how to build a React SPA using react-router-dom with Home, About and Contact pages and a shared navbar.

Outcome:
Successfully built the SPA with 3 routes and a shared layout.

---

### Task: Git and GitHub workflow

Prompt:
Explain how to initialize git, create branches, push code and create a pull request.

Outcome:
Initialized git, pushed code to GitHub and created a pull request.

---

### Task: Contact form with client-side validation

Prompt:
Create a contact form with Name, Email and Message fields using React with client-side validation.

Outcome:
Implemented validation and displayed error messages for invalid inputs.

---

## 30 June 2026

### Task: Configure ESLint and Prettier

Prompt:
How do I add Prettier to my React Vite project and make it work with ESLint?

Outcome:
Added a .prettierrc config file and a format script. Ran Prettier across all files. Lint passes clean.

---

### Task: Write unit tests for the contact form

Prompt:
How do I write unit tests for a React form using Vitest?

Outcome:
Set up Vitest and React Testing Library. Wrote 6 tests covering form validation, email errors, and nav links. All 6 passing.

---

## 3 July 2026

### Task: Build a FastAPI + SQLAlchemy REST API (Week 2)

Prompt:
Build a FastAPI backend with SQLAlchemy and SQLite. Create a User model and a Note model with a foreign key relationship. Implement full CRUD endpoints for Notes with Pydantic validation and correct HTTP status codes.

Outcome:
Created backend/ with User and Note ORM models, Pydantic schemas, and full CRUD on /notes (GET list, POST 201, GET by id, PUT 200, DELETE 204, 404 on missing). Also added /users endpoints. SQLite DB auto-created on startup.

---

### Task: Add ruff linter to the backend

Prompt:
How do I configure ruff as a linter for a FastAPI project using pyproject.toml?

Outcome:
Added pyproject.toml with ruff rules (E, W, F, I, UP). Fixed 5 issues — 4 long lines wrapped and 1 isort fix applied automatically. Ruff passes clean.

---

### Task: Write pytest tests for the Notes API

Prompt:
Write pytest tests for a FastAPI CRUD API using an in-memory SQLite test database and dependency injection to override get_db.

Outcome:
Created conftest.py with a TestClient fixture that overrides the DB session with a clean SQLite test database per test. Wrote 6 tests: create note (201), get all notes, get one note, update note, delete note (204), and 404 for missing note. All 6 passing.