from fastapi import FastAPI, HTTPException, Body
from app.repository import PostgresTaskRepository
from app.supabase_client import supabase


app = FastAPI()


repository = PostgresTaskRepository()


def signup_login_helper(data: dict = Body(...)) -> tuple[str, str]:
    email = data.get("email")
    password = data.get("password")

    if not email and not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are missing"
        )

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email is missing"
        )

    if not password:
        raise HTTPException(
            status_code=400,
            detail="Password is missing"
        )

    return (email, password)


@app.post("/auth/signup", status_code=201)
def sign_up(data: dict = Body(...)):
    email, password = signup_login_helper(data)

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return response.user


@app.post("/auth/login")
def log_in(data: dict = Body(...)) -> dict:
    email, password = signup_login_helper(data)

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token
    }


@app.get("/")
def read_root() -> dict:
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": [
            "GET /tasks?done=<bool>&search=<text>&sort=<field>",
            "GET /tasks/{task_id}",
            "POST /tasks",
            "PUT /tasks/{task_id}",
            "DELETE /tasks/{task_id}",
            "GET /health",
            "GET /stats",
            "POST /reset"
        ]
    }


@app.get("/health")
def read_status() -> dict:
    return {
        "status": "ok",
        "db": repository.db_status()
    }


@app.get("/tasks")
def read_tasks(
    done: bool | None = None,
    search: str | None = None,
    sort: str | None = None
) -> list[dict]:
    try:
        return repository.read_tasks(done, search, sort)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    

@app.get("/tasks/{task_id}")
def read_task(task_id: int) -> dict:
    task = repository.read_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return task


@app.get("/stats")
def read_stats() -> dict:
    return repository.read_stats()


@app.post("/tasks", status_code=201)
def create_task(data: dict = Body(...)) -> dict:
    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        raise HTTPException(
            status_code=400,
            detail="No title has been specified"
        )

    title = title.strip()

    return repository.create_task(title)


@app.post("/reset", status_code=201)
def reset_tasks() -> list[dict]:
    return repository.reset_tasks()

    
@app.put("/tasks/{task_id}")
def update_task(task_id: int, data: dict = Body(...)) -> dict:
    if (
        not isinstance(data, dict) or
        ("title" not in data and "done" not in data)
    ):
        raise HTTPException(
            status_code=400,
            detail="Empty or invalid body"
        )

    if "title" in data:
        title = data["title"]

        if not isinstance(title, str) or not title.strip():
            raise HTTPException(
                status_code=400,
                detail="The title should be a non-empty string"
            )
        
        data["title"] = title.strip()

    if "done" in data:
        done = data["done"]

        if not isinstance(done, bool):
            raise HTTPException(
                status_code=400,
                detail="Done should be a boolean value (true or false)"
            )

    task = repository.update_task(task_id, data)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    try:
        repository.delete_task(task_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )