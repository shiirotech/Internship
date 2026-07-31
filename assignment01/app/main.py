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
def read_tasks(done: bool | None = None, search: str | None = None):
    filtered = tasks
    if done is not None:
        filtered = [task for task in filtered if task["done"] == done]
    if search and search.strip():
        search = search.strip().lower()
        filtered = [task for task in filtered if search in task["title"].lower()]
    return filtered

@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
        
    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )

@app.get("/stats")
def read_stats():
    total = len(tasks)
    count_done = sum(1 for task in tasks if task["done"])
    count_open = total - count_done
    return {
        "total": total,
        "done": count_done,
        "open": count_open
    }

@app.post("/tasks", status_code=201)
def create_task(data: dict = Body(...)):
    title = data.get("title")
    if isinstance(title, str) and title.strip():
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

@app.put("/tasks/{task_id}")
def update_task(task_id: int, data: dict = Body(...)):
    if (
        not isinstance(data, dict) or
        ("title" not in data and "done" not in data)
    ):
        raise HTTPException(
            status_code=400,
            detail="Empty or invalid body"
        )

    has_title = "title" in data
    has_done = "done" in data

    if has_title:
        title = data["title"]

        if not isinstance(title, str) or not title.strip():
            raise HTTPException(
                status_code=400,
                detail="The title should be a non-empty string"
            )
        title = title.strip()

    if has_done:
        done = data["done"]

        if not isinstance(done, bool):
            raise HTTPException(
                status_code=400,
                detail="Done should be a boolean value (true or false)"
            )

    for task in tasks:
        if task["id"] == task_id:
            if has_title:
                task["title"] = title
            if has_done:
                task["done"] = done
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
        
    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )