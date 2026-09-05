from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

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

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title cannot be empty")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    done: Optional[bool] = None

# Initial data set
INITIAL_TASKS = [
    Task(id=1, title="Learn FastAPI", done=True),
    Task(id=2, title="Build my first CRUD API", done=False),
    Task(id=3, title="Push project to GitHub", done=False)
]

# In-memory database
tasks_db: List[Task] = list(INITIAL_TASKS)

# Base endpoints
@app.get("/", summary="API Root Info")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/stats", "/health", "/docs"]
    }

@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok"}

# Read endpoints (GET) with Filtering and Search
@app.get("/tasks", response_model=List[Task], summary="Get all tasks with optional filters")
def get_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    results = tasks_db
    if done is not None:
        results = [t for t in results if t.done == done]
    if search is not None:
        results = [t for t in results if search.lower() in t.title.lower()]
    return results

@app.get("/tasks/{task_id}", response_model=Task, summary="Get a task by ID")
def get_task(task_id: int):
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )

# Compute Stats Endpoint
@app.get("/stats", summary="Get task statistics")
def get_stats():
    total = len(tasks_db)
    done_count = sum(1 for t in tasks_db if t.done)
    return {
        "total": total,
        "done": done_count,
        "open": total - done_count
    }

# Seed & Reset Endpoint
@app.post("/reset", summary="Reset tasks to initial state")
def reset_tasks():
    global tasks_db
    tasks_db = [Task(**task.model_dump()) for task in INITIAL_TASKS]
    return {"message": "Database reset to initial state", "total": len(tasks_db)}

# Create endpoint (POST)
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

# Update & Delete endpoints (PUT & DELETE)
@app.put("/tasks/{task_id}", response_model=Task, summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body must contain at least title or done status"
        )

    for task in tasks_db:
        if task.id == task_id:
            if payload.title is not None:
                clean_title = payload.title.strip()
                if not clean_title:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Title cannot be empty or blank string"
                    )
                task.title = clean_title
            if payload.done is not None:
                task.done = payload.done
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(task_id: int):
    for idx, task in enumerate(tasks_db):
        if task.id == task_id:
            tasks_db.pop(idx)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )