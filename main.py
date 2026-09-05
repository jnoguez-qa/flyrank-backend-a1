from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(
    title="Task API",
    description="In-memory CRUD API for FlyRank AI Internship W2-A1",
    version="1.0"
)

# Data models
class Task(BaseModel):
    id: int
    title: str
    done: bool = False

# Schema for creating tasks (validates non-empty title)
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title cannot be empty")

# In-memory database pre-filled with 3 sample tasks
tasks_db: List[Task] = [
    Task(id=1, title="Learn FastAPI", done=True),
    Task(id=2, title="Build my first CRUD API", done=False),
    Task(id=3, title="Push project to GitHub", done=False)
]

# Stage 1: Base endpoints
@app.get("/", summary="API Root Info")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/health", "/docs"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok"}

# Stage 2: Read endpoints (GET)
@app.get("/tasks", response_model=List[Task], summary="Get all tasks")
def get_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", response_model=Task, summary="Get a task by ID")
def get_task(task_id: int):
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )

# Stage 3: Create endpoint (POST)
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(payload: TaskCreate):
    clean_title = payload.title.strip()
    if not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty or blank string"
        )
    
    new_id = max([t.id for t in tasks_db], default=0) + 1
    new_task = Task(id=new_id, title=clean_title, done=False)
    tasks_db.append(new_task)
    return new_task