from fastapi import FastAPI, HTTPException

app = FastAPI()

tasks = [
    {
        "id": 1,
        "title": "First task",
        "done": True
    },
    {
        "id": 2,
        "title": "Second task",
        "done": True
    },
    {
        "id": 3,
        "title": "Third task",
        "done": False
    }
]

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def read_status():
    return {"status": "ok"}

@app.get("/tasks")
def read_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def read_item(task_id: int):
    for item in tasks:
        if item["id"] == task_id:
            return item
        
    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )