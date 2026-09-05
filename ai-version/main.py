"""

A production-ready in-memory CRUD API with:
- Comprehensive input validation
- Proper HTTP status codes
- Error handling with descriptive messages
- Type safety with Pydantic models
- Interactive OpenAPI documentation at /docs
- Request/response validation
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

# ============================================================================
# Models and Enums
# ============================================================================

class TaskStatus(str, Enum):
    """Task completion status"""
    PENDING = "pending"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    """Base model for task validation"""
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Task title (required, 1-255 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional task description"
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Task completion status"
    )

    @validator('title')
    def title_must_not_be_empty_or_whitespace(cls, v):
        """Ensure title is not empty or whitespace"""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or contain only whitespace")
        return v.strip()

    @validator('description', pre=True, always=True)
    def description_validation(cls, v):
        """Ensure description is valid"""
        if v is not None and isinstance(v, str):
            return v.strip() if v.strip() else None
        return v

    class Config:
        schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive API docs",
                "status": "pending"
            }
        }


class TaskCreate(TaskBase):
    """Model for creating a new task"""
    pass


class TaskUpdate(BaseModel):
    """Model for updating a task"""
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Task title (1-255 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Task description"
    )
    status: Optional[TaskStatus] = Field(
        None,
        description="Task completion status"
    )

    @validator('title')
    def title_must_not_be_empty_or_whitespace(cls, v):
        """Ensure title is not empty or whitespace if provided"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Title cannot be empty or contain only whitespace")
            return v.strip()
        return v

    @validator('description', pre=True, always=True)
    def description_validation(cls, v):
        """Ensure description is valid"""
        if v is not None and isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v

    class Config:
        schema_extra = {
            "example": {
                "title": "Updated task title",
                "status": "completed"
            }
        }


class Task(TaskBase):
    """Complete task model with metadata"""
    id: str = Field(
        ...,
        description="Unique task identifier (UUID)"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when task was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when task was last updated"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Complete project documentation",
                "description": "Write comprehensive API docs",
                "status": "pending",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")


# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Task Management API",
    description="A robust RESTful API for managing tasks with full CRUD operations",
    version="1.0.0",
    contact={
        "name": "API Support",
        "url": "https://api.example.com",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================================
# In-Memory Database
# ============================================================================

class TaskStore:
    """Simple in-memory task storage with validation"""
    
    def __init__(self):
        self.tasks: dict[str, dict] = {}
        self._initialize_starter_tasks()
    
    def _initialize_starter_tasks(self):
        """Initialize with starter tasks"""
        starter_tasks = [
            {
                "title": "Review API documentation",
                "description": "Ensure all endpoints are documented",
                "status": TaskStatus.PENDING
            },
            {
                "title": "Set up CI/CD pipeline",
                "description": "Configure automated testing and deployment",
                "status": TaskStatus.PENDING
            },
            {
                "title": "Write unit tests",
                "description": "Achieve 80% code coverage",
                "status": TaskStatus.COMPLETED
            },
            {
                "title": "Deploy to production",
                "description": "Release v1.0.0",
                "status": TaskStatus.COMPLETED
            },
            {
                "title": "Gather user feedback",
                "description": "Collect feedback from beta testers",
                "status": TaskStatus.PENDING
            }
        ]
        
        for task_data in starter_tasks:
            task_id = str(uuid.uuid4())
            now = datetime.now()
            self.tasks[task_id] = {
                "id": task_id,
                "title": task_data["title"],
                "description": task_data["description"],
                "status": task_data["status"],
                "created_at": now,
                "updated_at": now
            }
    
    def get_all(self) -> List[dict]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def get_by_id(self, task_id: str) -> Optional[dict]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def create(self, task_data: TaskCreate) -> dict:
        """Create new task"""
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = {
            "id": task_id,
            "title": task_data.title,
            "description": task_data.description,
            "status": task_data.status,
            "created_at": now,
            "updated_at": now
        }
        
        self.tasks[task_id] = task
        return task
    
    def update(self, task_id: str, task_data: TaskUpdate) -> Optional[dict]:
        """Update existing task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        now = datetime.now()
        
        # Update only provided fields
        if task_data.title is not None:
            task["title"] = task_data.title
        if task_data.description is not None:
            task["description"] = task_data.description
        if task_data.status is not None:
            task["status"] = task_data.status
        
        task["updated_at"] = now
        
        return task
    
    def delete(self, task_id: str) -> bool:
        """Delete task by ID"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False


# Initialize task store
task_store = TaskStore()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get(
    "/tasks",
    response_model=List[Task],
    summary="List all tasks",
    description="Retrieve all tasks from the database",
    tags=["Tasks"]
)
def get_tasks(
    status: Optional[TaskStatus] = Query(
        None,
        description="Filter by status (optional)"
    )
) -> List[Task]:
    """
    Get all tasks, optionally filtered by status.
    
    **Query Parameters:**
    - `status`: Optional filter (pending or completed)
    
    **Returns:**
    - List of all tasks or filtered by status
    """
    all_tasks = task_store.get_all()
    
    if status:
        all_tasks = [t for t in all_tasks if t["status"] == status]
    
    return all_tasks


@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Get a specific task",
    description="Retrieve a single task by its ID",
    tags=["Tasks"],
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Task not found"
        }
    }
)
def get_task(task_id: str) -> Task:
    """
    Get a specific task by ID.
    
    **Path Parameters:**
    - `task_id`: UUID of the task
    
    **Returns:**
    - Task object
    
    **Raises:**
    - 404 Not Found: If task ID doesn't exist
    """
    task = task_store.get_by_id(task_id)
    
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID '{task_id}' not found"
        )
    
    return task


@app.post(
    "/tasks",
    response_model=Task,
    status_code=201,
    summary="Create a new task",
    description="Create a new task with title and optional description",
    tags=["Tasks"],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid task data (empty title)"
        }
    }
)
def create_task(task: TaskCreate) -> Task:
    """
    Create a new task.
    
    **Request Body:**
    - `title`: Task title (required, 1-255 characters, cannot be empty or whitespace)
    - `description`: Optional description (max 2000 characters)
    - `status`: Optional status (pending or completed, defaults to pending)
    
    **Returns:**
    - 201 Created: The newly created task object
    
    **Raises:**
    - 400 Bad Request: If title is missing, empty, or only whitespace
    """
    created_task = task_store.create(task)
    return created_task


@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Update an existing task",
    description="Update one or more fields of an existing task",
    tags=["Tasks"],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid task data"
        },
        404: {
            "model": ErrorResponse,
            "description": "Task not found"
        }
    }
)
def update_task(task_id: str, task: TaskUpdate) -> Task:
    """
    Update a task by ID.
    
    **Path Parameters:**
    - `task_id`: UUID of the task to update
    
    **Request Body:**
    - `title`: Optional new title (1-255 characters, cannot be empty or whitespace)
    - `description`: Optional new description (max 2000 characters)
    - `status`: Optional new status (pending or completed)
    
    **Returns:**
    - 200 OK: The updated task object
    
    **Raises:**
    - 400 Bad Request: If title is empty or only whitespace
    - 404 Not Found: If task ID doesn't exist
    """
    # Verify task exists
    if task_store.get_by_id(task_id) is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID '{task_id}' not found"
        )
    
    # Update task
    updated_task = task_store.update(task_id, task)
    
    return updated_task


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Delete a task by ID",
    tags=["Tasks"],
    responses={
        204: {
            "description": "Task deleted successfully"
        },
        404: {
            "model": ErrorResponse,
            "description": "Task not found"
        }
    }
)
def delete_task(task_id: str) -> None:
    """
    Delete a task by ID.
    
    **Path Parameters:**
    - `task_id`: UUID of the task to delete
    
    **Returns:**
    - 204 No Content: Task deleted successfully
    
    **Raises:**
    - 404 Not Found: If task ID doesn't exist
    """
    deleted = task_store.delete(task_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID '{task_id}' not found"
        )


# ============================================================================
# Health Check and Info Endpoints
# ============================================================================

@app.get(
    "/health",
    summary="Health check",
    description="Check if API is running",
    tags=["System"]
)
def health_check():
    """
    Health check endpoint.
    
    **Returns:**
    - Status: ok
    - Timestamp: Current server time
    - Task count: Number of tasks in database
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "task_count": len(task_store.get_all())
    }


@app.get(
    "/info",
    summary="API information",
    description="Get information about the API",
    tags=["System"]
)
def get_info():
    """
    Get API information and statistics.
    
    **Returns:**
    - API name, version, and description
    - Statistics about stored tasks
    """
    all_tasks = task_store.get_all()
    pending_count = sum(1 for t in all_tasks if t["status"] == TaskStatus.PENDING)
    completed_count = sum(1 for t in all_tasks if t["status"] == TaskStatus.COMPLETED)
    
    return {
        "api_name": "Task Management API",
        "version": "1.0.0",
        "description": "Robust RESTful API for managing tasks",
        "statistics": {
            "total_tasks": len(all_tasks),
            "pending_tasks": pending_count,
            "completed_tasks": completed_count
        },
        "documentation": "/docs",
        "alternative_documentation": "/redoc"
    }


# ============================================================================
# Custom Exception Handler
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc):
    """Handle validation errors gracefully"""
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "status_code": 400
        }
    )


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get(
    "/",
    tags=["System"]
)
def root():
    """
    Welcome to Task Management API.
    
    **Quick Links:**
    - Interactive Docs: `/docs`
    - ReDoc: `/redoc`
    - OpenAPI JSON: `/openapi.json`
    - Health Check: `/health`
    - API Info: `/info`
    """
    return {
        "message": "Welcome to Task Management API",
        "version": "1.0.0",
        "documentation": {
            "interactive": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": "/health",
            "info": "/info"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "task_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )