from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# Importamos las funciones de conexión que creamos en database.py
from database import get_db_connection, init_db


# ============================================================================
# Lifespan Event (Inicializa la BD en Docker al arrancar la API)
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ejecuta init_db() para crear la tabla 'tasks' y los datos de prueba si no existen
    init_db()
    yield


# ============================================================================
# Instancia de FastAPI
# ============================================================================
app = FastAPI(
    title="Task API - PostgreSQL",
    description="PostgreSQL CRUD API running in Docker for FlyRank AI Internship",
    version="3.0",
    lifespan=lifespan,
)


# ============================================================================
# Modelos Pydantic
# ============================================================================
class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title cannot be empty")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    done: Optional[bool] = None


# ============================================================================
# Endpoints de la API
# ============================================================================


@app.get("/", summary="API Root Info", tags=["System"])
def read_root():
    return {
        "message": "API running with PostgreSQL in Docker",
        "docs": "/docs",
    }


# 1. OBTENER TODAS LAS TAREAS (GET)
@app.get(
    "/tasks",
    response_model=List[Task],
    summary="Get all tasks",
    tags=["Tasks"],
)
def get_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id ASC;")
            rows = cur.fetchall()
            return rows


# 2. OBTENER UNA TAREA POR ID (GET)
@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Get a task by ID",
    tags=["Tasks"],
)
def get_task(task_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": "Task not found"},
                )
            return row


# 3. CREAR UNA NUEVA TAREA (POST)
@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    tags=["Tasks"],
)
def create_task(payload: TaskCreate):
    clean_title = payload.title.strip()
    if not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Title cannot be empty"},
        )

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Usamos RETURNING id, title, done para obtener el objeto insertado directamente en Postgres
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                (clean_title, False),
            )
            new_task = cur.fetchone()
            conn.commit()
            return new_task


# 4. ACTUALIZAR UNA TAREA (PUT)
@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Update a task",
    tags=["Tasks"],
)
def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Request body must contain title or done"},
        )

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Verificar si existe la tarea
            cur.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
            existing = cur.fetchone()
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": "Task not found"},
                )

            new_title = (
                payload.title.strip()
                if payload.title is not None
                else existing["title"]
            )
            if payload.title is not None and not new_title:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": "Title cannot be empty"},
                )

            new_done = (
                payload.done if payload.done is not None else existing["done"]
            )

            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
                (new_title, new_done, task_id),
            )
            updated_task = cur.fetchone()
            conn.commit()
            return updated_task


# 5. ELIMINAR UNA TAREA (DELETE)
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    tags=["Tasks"],
)
def delete_task(task_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
            existing = cur.fetchone()
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": "Task not found"},
                )

            cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
            conn.commit()
    return None