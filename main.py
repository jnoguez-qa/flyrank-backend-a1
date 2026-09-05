from fastapi import FastAPI

app = FastAPI(
    title="Task API",
    description="In-memory CRUD API for FlyRank AI Internship W2-A1",
    version="1.0"
)

# Stage 0 & 1: Root & Health Check Endpoints
@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/health", "/docs"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}