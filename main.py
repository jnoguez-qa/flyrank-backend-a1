from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Task API",
    description="In-memory CRUD API for FlyRank AI Internship W2-A1",
    version="1.0"
)

# Modelo de datos para una tarea
class Task(BaseModel):
    id: int
    title: str
    done: bool = False

# Base de datos en memoria prellenada con 3 tareas de ejemplo
tasks_db: List[Task] = [
    Task(id=1, title="Aprender FastAPI", done=True),
    Task(id=2, title="Construir mi primera API CRUD", done=False),
    Task(id=3, title="Subir el proyecto a GitHub", done=False)
]

# Stage 1: Endpoints base
@app.get("/", summary="Información de la API")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/health", "/docs"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok"}

# Stage 2: Endpoints de lectura (GET)
@app.get("/tasks", response_model=List[Task], summary="Obtener todas las tareas")
def get_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", response_model=Task, summary="Obtener una tarea por ID")
def get_task(task_id: int):
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )