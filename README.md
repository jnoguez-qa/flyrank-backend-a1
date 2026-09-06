# Task API — FlyRank Backend Internship (W2-A1)

A RESTful in-memory CRUD API built with Python and FastAPI for managing a to-do list.

## Features
- **In-Memory Storage**: Initialized with sample tasks (no external database required).
- **Full CRUD Support**: Create, Read, Update, and Delete operations.
- **Input Validation**: Rejects empty task titles with HTTP 400.
- **Auto-Generated Interactive Docs**: Available via Swagger UI at `/docs`.
- **Query Filtering & Search**: Filter by completion status (`?done=true`) or search title keywords (`?search=FastAPI`).
- **Server Computation**: Stats endpoint returning real-time aggregated metrics.
- **State Reset**: POST `/reset` endpoint to restore starter tasks.

---

## How to Install and Run

1. **Clone the repository:**
   git clone https://github.com/jnoguez-qa/flyrank-backend-a1.git
   cd flyrank-backend-a1

2. **Create and activate a virtual environment:**
   python -m venv venv
   .\venv\Scripts\Activate.ps1

3. **Install dependencies:**
   pip install -r requirements.txt

4. **Start the server:**
   python -m uvicorn main:app --reload --port 8000

---

## API Endpoints Table

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | API Information | `200 OK` |
| **GET** | `/health` | Server Health Check | `200 OK` |
| **GET** | `/tasks` | List all tasks (supports `?done=bool` & `?search=str`) | `200 OK` |
| **GET** | `/tasks/{id}` | Get single task by ID | `200 OK` / `404 Not Found` |
| **GET** | `/stats` | Get total, done, and open task metrics | `200 OK` |
| **POST** | `/reset` | Reset database to initial 3 sample tasks | `200 OK` |
| **POST** | `/tasks` | Create a new task | `201 Created` / `400 Bad Request` |
| **PUT** | `/tasks/{id}` | Update task title or status | `200 OK` / `400 Bad Request` / `404 Not Found` |
| **DELETE** | `/tasks/{id}` | Delete task by ID | `204 No Content` / `404 Not Found` |

---

## The Mortality Experiment
When creating new tasks and subsequently restarting the server process, all newly created data vanishes, reverting back strictly to the 3 initial tasks. This occurs because state is stored purely within volatile RAM memory without persistent disk storage or a database engine; restarting the server process completely clears and re-initializes memory space.

---

## Sample `curl` Output

$ curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '"{""title"":""Buy milk""}"'

HTTP/1.1 201 Created
date: Sat, 05 Sep 2026 16:24:16 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}

---

## Swagger UI Screenshot

![Swagger UI](swagger.png)

---

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

## Database Implementation (SQLite)

- **Why SQLite?** It is lightweight, serverless, requires zero configuration, and stores data in a single file (`tasks.db`) that persists across server restarts.
- **Database Location:** `tasks.db` at the project root (ignored by Git so every clone starts fresh)[cite: 1].
- **How to Run:**
  ```bash
  uvicorn main:app --reload

  Example SQL Query executed manually:
  SELECT * FROM tasks WHERE done = 1;