from fastapi import FastAPI, HTTPException, Body

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
def read_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
        
    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )

@app.post("/tasks", status_code=201)
def add_task(data: dict = Body(...)):
    title = data.get("title")
    if title and title.strip():
        tasks.append({
            "id": tasks[-1]["id"] + 1,
            "title": title,
            "done": False
        })

        return tasks[-1]
    
    raise HTTPException(
        status_code=400,
        detail="No title has been specified"
    )