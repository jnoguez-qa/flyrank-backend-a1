# Task API — FlyRank Backend Internship (W3-A3)

A RESTful CRUD API built with Python, FastAPI, and PostgreSQL running inside Docker containers for persistent data storage.

## Features
- **PostgreSQL Database**: Data persisted in PostgreSQL 16 running inside Docker container (`taskdb`) with host volume mapping (`taskdata`).
- **Connection Management**: Environment-based configuration using `.env` via `python-dotenv` and lightweight database driver `psycopg`.
- **Full CRUD Support**: Create, Read, Update, and Delete operations executed with direct raw SQL queries (`SELECT`, `INSERT`, `UPDATE`, `DELETE`).
- **Input Validation**: Rejects empty or whitespace-only task titles with HTTP 400 Bad Request.
- **Auto-Generated Interactive Docs**: Available via Swagger UI at `/docs` and ReDoc at `/redoc`.
- **Lifespan Initialization**: Database table structure and seed tasks automatically checked and initialized on application startup.

---

## Prerequisites
- Docker & Docker Desktop running on your machine.
- Python 3.10+
- `venv` (Python virtual environment)

---

## How to Install and Run

1. **Clone the repository:**
   git clone https://github.com/jnoguez-qa/flyrank-backend-a1.git
   cd flyrank-backend-a1

2. **Run PostgreSQL Container in Docker:**
   docker run -d --name taskdb -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=tasks -v taskdata:/var/lib/postgresql/data postgres:16

3. **Configure Environment Variables:**
   Copy `.env.example` to create `.env`:
   cp .env.example .env
   *Note: Ensure `.env` contains `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tasks`*

4. **Create and activate virtual environment:**
   python -m venv venv
   .\venv\Scripts\Activate.ps1

5. **Install dependencies:**
   pip install -r requirements.txt

6. **Start the server:**
   uvicorn main:app --reload --port 8000

---

## Database Schema & Persistence Verification

### Database Schema (`tasks`)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incrementing identifier |
| `title` | `TEXT` | `NOT NULL` | Task title |
| `done` | `BOOLEAN` | `DEFAULT FALSE` | Completion status |

### Verify Database directly in Docker:
docker exec -it taskdb psql -U postgres -d tasks -c "SELECT * FROM tasks;"

---

## API Endpoints Table

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | API Root Information | `200 OK` |
| **GET** | `/tasks` | List all tasks from PostgreSQL | `200 OK` |
| **GET** | `/tasks/{id}` | Get single task by ID | `200 OK` / `404 Not Found` |
| **POST** | `/tasks` | Create a new task | `201 Created` / `400 Bad Request` |
| **PUT** | `/tasks/{id}` | Update task title or completion status | `200 OK` / `400 Bad Request` / `404 Not Found` |
| **DELETE** | `/tasks/{id}` | Delete task by ID | `204 No Content` / `404 Not Found` |

---

## Sample `curl` Output

$ curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Probar PostgreSQL en Docker"}'

HTTP/1.1 201 Created
date: Sun, 06 Sep 2026 21:40:34 GMT
server: uvicorn
content-length: 56
content-type: application/json

{"id":5,"title":"Probar PostgreSQL en Docker","done":false}

---

## Swagger UI Screenshot

![Swagger UI](swagger.png)

---

## Stage 7 — AI vs Me

### Prompt Used
> "Build a RESTful in-memory CRUD API in Python using FastAPI for managing a task list. Implement endpoints for GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, and DELETE /tasks/{id}. Ensure POST and PUT validate task titles and return HTTP 400 Bad Request for empty or missing titles. Return HTTP 404 for non-existent IDs, HTTP 201 for POST, and HTTP 204 for DELETE. Store tasks in an in-memory list with a few starter items. Automatically generate interactive documentation at /docs."

### Code Review & Comparison
1. **What the AI did better:** It provided extremely thorough docstrings, explicit type annotations, and a comprehensive suite of unit tests out of the box.
2. **What it got wrong/ignored:** It severely over-engineered the assignment, creating over 11 files and 1,400+ lines of code for a simple single-file in-memory CRUD task. Furthermore, for invalid/empty request bodies, it relied on standard Pydantic validation (which raises `HTTP 422 Unprocessable Entity`) instead of explicitly handling custom `HTTP 400 Bad Request` exceptions as requested.
3. **What my prompt forgot & AI decisions:** The prompt didn't specify a minimalist scope, so the AI assumed enterprise-level requirements and added extraneous test suites, multi-file module structures, and heavy logging frameworks that were unnecessary for this stage.

### Refined Prompt Takeaway
When prompting AI for backend modules, specifying constraints on code architecture (e.g., *"keep implementation lightweight in a single main.py file without external test suites"*) is as vital as specifying endpoint business logic.

---

## Database Migration Journey

- **Stage 1 (In-Memory)**: Volatile RAM storage where data resets on server restart.
- **Stage 2 (SQLite)**: File-based persistence (`tasks.db`) using Python's built-in `sqlite3` module.
- **Stage 3 (PostgreSQL in Docker)**: Enterprise-grade relational database engine running in an isolated Docker container with host-mounted volume (`taskdata`) ensuring full data durability, driver abstraction via `psycopg`, and environment variable management using `python-dotenv`.