# Neighborhood Library App

A full-stack library management application built with **FastAPI**, **PostgreSQL**, and **Next.js**.

The application allows librarians to manage books, members, and borrowings through a REST API and a web-based staff portal.

---

## Tech Stack

### Backend

* Python 3.13
* FastAPI
* SQLAlchemy 2.x
* PostgreSQL
* Pydantic v2
* uv

### Frontend

* React
* Next.js

---

## Features

### ✅ Implemented

* Books CRUD API
* Members CRUD API
* Borrowings API

  * Create borrowing
  * Return book
  * Active borrowings
  * Returned borrowings
  * Overdue borrowings
  * Borrowing history by member
  * Borrowing history by book
  * Current borrower lookup
  * Book availability lookup
* PostgreSQL database integration
* SQLAlchemy ORM models
* Request and response validation using Pydantic
* Unit and integration tests
* Next.js staff portal

### 🚧 In Progress

* Authentication
* Docker support

---

## Project Structure

```text
backend/
│
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── database.py
│   ├── config.py
│   └── main.py
│
└── tests/

database/
│
└── schema.sql

frontend/
│
├── src/
│   ├── app/
│   ├── components/
│   └── lib/
│
├── package.json
└── next.config.ts

pyproject.toml
uv.lock
README.md
```

---

# Backend Setup

## 1. Clone the repository

```bash
git clone <repository-url>
cd neighbourhood_library
```

---

## 2. Install uv

If you don't already have `uv` installed:

```bash
pip install uv
```

Alternatively, install it using `pipx`:

```bash
pipx install uv
```

---

## 3. Install dependencies

Install all project dependencies:

```bash
uv sync
```

This command automatically:

* creates a virtual environment (`.venv`) if one doesn't exist,
* installs all dependencies from `uv.lock`,
* ensures a reproducible environment.

---

## 4. Configure environment variables

Create a `.env` file in the project root.

Example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=library
DB_USER=postgres
DB_PASSWORD=your_password
```

---

## 5. Create the database

Create a PostgreSQL database and execute:

```text
database/schema.sql
```

to create all required tables.

---

## 6. Run the backend

```bash
uv run uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

## 7. Run backend tests

The backend tests use a dedicated PostgreSQL database and refuse to run if the configured database name does not end with `_test`.

Copy:

```text
.env.test.example
```

to

```text
.env.test
```

Configure your PostgreSQL credentials and ensure the test database exists.

Run the test suite:

```bash
uv run pytest backend/tests
```

The test suite truncates and reseeds only the configured test database before each test.

> **Do not point `.env.test` to your development database.**

---

## Dependency Management

This project uses **uv** for dependency management.

| Task                                       | Command                  |
| ------------------------------------------ | ------------------------ |
| Install dependencies                       | `uv sync`                |
| Add a dependency                           | `uv add <package>`       |
| Add a development dependency               | `uv add --dev <package>` |
| Remove a dependency                        | `uv remove <package>`    |
| Regenerate lock file                       | `uv lock`                |
| Upgrade dependencies                       | `uv lock --upgrade`      |
| Run any command in the project environment | `uv run <command>`       |

Project dependency files:

* `pyproject.toml` — project metadata and dependency specifications
* `uv.lock` — locked dependency versions for reproducible builds

---

# API Status

| Resource   | Status     |
| ---------- | ---------- |
| Books      | ✅ Complete |
| Members    | ✅ Complete |
| Borrowings | ✅ Complete |
| Frontend   | ✅ Complete |

---

# Frontend Setup

The staff portal is a **Next.js** application located in the `frontend/` directory.

The frontend proxies requests to the FastAPI backend using Next.js rewrites, so no CORS configuration is required.

## Prerequisites

* Node.js 18+
* npm

---

## 1. Install dependencies

```bash
cd frontend
npm install
```

---

## 2. Configure environment

Copy the example environment file:

```bash
cp .env.local.example .env.local
```

Default configuration:

```env
BACKEND_URL=http://localhost:8000
```

---

## 3. Run the frontend

Start the backend first, then run:

```bash
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

## Frontend Pages

| Page       | Path          | Description                                                               |
| ---------- | ------------- | ------------------------------------------------------------------------- |
| Dashboard  | `/`           | Summary statistics and recent borrowings                                  |
| Books      | `/books`      | Manage books, availability, and borrowing history                         |
| Members    | `/members`    | Manage members and view active borrowings                                 |
| Borrowings | `/borrowings` | Record loans and returns, filter active, overdue, and returned borrowings |

---

## Production Build

```bash
cd frontend
npm run build
npm start
```
