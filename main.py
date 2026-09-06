import sqlite3
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# 1. Configuración de Base de Datos
def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER DEFAULT 0
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Aprender FastAPI", 1),
                    ("Conectar SQLite a FastAPI", 0),
                    ("Completar Assignment 2", 0)
                ]
            )

init_db()

# 2. Instancia de FastAPI (SÓLO UNA)
app = FastAPI(
    title="Task API",
    description="SQLite CRUD API for FlyRank AI Internship W3-A2",
    version="2.0"
)

# 3. Modelos
class Task(BaseModel):
    id: int
    title: str
    done: bool = False

# 4. Endpoints de lectura (Stage 1)
@app.get("/", summary="API Root Info")
def read_root():
    return {"message": "API running"}

@app.get("/tasks", response_model=List[Task], summary="Get all tasks")
def get_tasks():
    with get_db() as conn:
        rows = conn.execute("SELECT id, title, done FROM tasks").fetchall()
        return [Task(id=r["id"], title=r["title"], done=bool(r["done"])) for r in rows]

@app.get("/tasks/{task_id}", response_model=Task, summary="Get a task by ID")
def get_task(task_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Task not found"}
            )
        return Task(id=row["id"], title=row["title"], done=bool(row["done"]))

    
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title cannot be empty")

# --- STAGE 2: CREATE ENDPOINT (POST) ---

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(payload: TaskCreate):
    clean_title = payload.title.strip()
    if not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Title cannot be empty"}
        )

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (clean_title, 0)
        )
        new_id = cursor.lastrowid
        row = conn.execute("SELECT id, title, done FROM tasks WHERE id = ?", (new_id,)).fetchone()
        
    return Task(id=row["id"], title=row["title"], done=bool(row["done"]))   