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

### Task: Build a REST API backend

Prompt:
How do I build a simple REST API using FastAPI with a database?

Outcome:
Built a FastAPI backend with User and Note models using SQLAlchemy and SQLite. 
Full CRUD endpoints for notes working. Auto-generated docs available at /docs.

---

### Task: Add a linter to the backend

Prompt:
How do I add a linter to a Python FastAPI project?

Outcome:
Set up ruff using pyproject.toml. Fixed a few style issues. Clean pass.

---

### Task: Write backend tests

Prompt:
How do I write tests for a FastAPI API?

Outcome:
Set up pytest with a test database. Wrote 6 tests covering creating, 
reading, updating, deleting notes, and a 404 case. All passing.

---

## 4 July 2026

### Task: Add JWT authentication to the backend

Prompt:
How do I add login and registration to a FastAPI app using JWT tokens?

Outcome:
Added register and login endpoints. Passwords are hashed with bcrypt. Login returns a JWT token. All notes endpoints now require a valid token.

---

### Task: Add role-based authorization

Prompt:
How do I restrict certain API endpoints to admin users only in FastAPI?

Outcome:
Added an is_admin field to the User model. Created a require_admin dependency. Admin users can access GET /notes/all to see every note. Regular users get a 403.

---

### Task: Write an integration test

Prompt:
How do I write an integration test for a FastAPI app that tests the full user flow?

Outcome:
Wrote a test that registers a user, logs in, gets a token, creates a note, and fetches it back. Each step checks the status code and response data.

---

### Task: Connect the React frontend to the FastAPI backend

Prompt:
How do I connect a React frontend to a FastAPI backend with JWT authentication?

Outcome:
Added Login and Register pages. JWT token stored in localStorage after login. Notes page fetches from the API and supports create, edit and delete. Navbar shows a logout button when logged in.

## 21 July 2026

### Task: Build an AI research agent

Prompt:
How do I build an AI agent in Python that can search the web and answer multi-step questions?

Outcome:
Built an agent using the Anthropic API with a ReAct loop. Agent decides which tool to call, calls it, and keeps going until it has a final answer.

---

### Task: Add memory to the agent

Prompt:
How do I make an AI agent remember things from earlier in the conversation?

Outcome:
Built a Memory class that stores facts as strings and injects them into the system prompt so the agent can recall them later.

---

### Task: Add hooks for logging tool calls

Prompt:
How do I log every tool call an AI agent makes with timestamps?

Outcome:
Added before_tool_call and after_tool_call functions that print to the console and write to agent_log.txt with timestamps and duration in ms.

---

### Task: Add a file-read plugin

Prompt:
How do I let an AI agent read .txt and .pdf files?

Outcome:
Built a read_file tool using pypdf for PDFs and plain open() for text files. Output is capped at 3000 characters.

---

### Task: Demo multi-hop agent

Prompt:
How do I test that my agent can chain multiple tool calls to answer a complex question?

Outcome:
Wrote a demo with 3 questions: web search + remember, file read, and memory recall. All 3 working correctly.