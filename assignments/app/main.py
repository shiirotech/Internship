import json
from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.repository import PostgresTaskRepository
from app.supabase_client import supabase
from app.redis_cl import redis_client
from random import randint


app = FastAPI()
security = HTTPBearer()


repository = PostgresTaskRepository()


def signup_login_helper(data: dict = Body(...)) -> tuple[str, str]:
    email = data.get("email")
    password = data.get("password")

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


def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security)):
    token = authorization.credentials

    try:
        response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return response.user


def get_version(version_key: str) -> int:
    version = redis_client.get(version_key)

    if version is None:
        version = 1
        redis_client.set(version_key, version)
    else:
        version = int(version)

    return version


def invalidate_user_cache(user_id: str) -> None:
    redis_client.incr(f"tasks_version:{user_id}")
    redis_client.incr(f"stats_version:{user_id}")


@app.post("/auth/signup", status_code=201)
def sign_up(data: dict = Body(...)):
    email, password = signup_login_helper(data)

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid format"
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


@app.post("/auth/logout", status_code=204)
def log_out(_: object = Depends(get_current_user)) -> None:
    supabase.auth.sign_out()


@app.post("/auth/refresh")
def refresh_access_token(data: dict = Body(...)) -> dict:
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Refresh token required"
        )

    try:
        refreshed = supabase.auth.refresh_session(refresh_token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )

    return {
        "access_token": refreshed.session.access_token,
        "refresh_token": refreshed.session.refresh_token
    }    
    

@app.get("/public/info")
def public_info() -> dict:
    return { "message": "Welcome stranger! This info is public." }


@app.get("/protected/profile")
def protected_profile(user=Depends(get_current_user)):
    return user


@app.get("/protected/dashboard")
def protected_dashboard(user=Depends(get_current_user)) -> dict:
    return {
        "user": {
            "id": user.id,
            "email": user.email
        },
        "message": f"Welcome, {user.email}!"
    }


@app.get("/protected/admin")
def protected_admin(user=Depends(get_current_user)) -> dict:
    if user.email != "admin@gmail.com":
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )
    
    return { "message": "Welcome, admin!" }


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
            "POST /reset",
            "POST /auth/signup",
            "POST /auth/login",
            "POST /auth/logout",
            "POST /auth/refresh",
            "GET /public/info",
            "GET /protected/profile",
            "GET /protected/dashboard",
            "GET /protected/admin"
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
    user=Depends(get_current_user),
    done: bool | None = None,
    search: str | None = None,
    sort: str | None = None
) -> list[dict]:
    version_key = f"tasks_version:{user.id}"
    version = get_version(version_key)

    cache_key = f"tasks:{user.id}:v{version}:done={done}:search={search}:sort={sort}"
    cached = redis_client.get(cache_key)

    if cached is not None:
        print("CACHE HIT")
        return json.loads(cached)

    print("CACHE MISS")
    
    try:
        tasks = repository.read_tasks(user.id, done, search, sort)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    ttl = randint(50, 70)
    
    redis_client.set(
        cache_key,
        json.dumps(tasks, default=str),
        ex=ttl
    )

    print("CACHE SET")

    return tasks
    

@app.get("/tasks/{task_id}")
def read_task(task_id: int, user=Depends(get_current_user)) -> dict:
    cache_key = f"task:{user.id}:{task_id}"
    cached = redis_client.get(cache_key)

    if cached is not None:
        print("CACHE HIT")
        return json.loads(cached)

    print("CACHE MISS")
    
    task = repository.read_task(task_id, user.id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    ttl = randint(50, 70)
        
    redis_client.set(
        cache_key,
        json.dumps(task, default=str),
        ex=ttl
    )

    return task


@app.get("/stats")
def read_stats(user=Depends(get_current_user)) -> dict:
    version_key = f"stats_version:{user.id}"
    version = get_version(version_key)

    cache_key = f"stats:{user.id}:v{version}"
    cached = redis_client.get(cache_key)

    if cached is not None:
        print("CACHE HIT")
        return json.loads(cached)

    print("CACHE MISS")

    stats = repository.read_stats(user.id)

    ttl = randint(50, 70)

    redis_client.set(
        cache_key,
        json.dumps(stats, default=str),
        ex=ttl
    )

    return stats


@app.post("/tasks", status_code=201)
def create_task(data: dict = Body(...), user=Depends(get_current_user)) -> dict:
    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        raise HTTPException(
            status_code=400,
            detail="No title has been specified"
        )

    title = title.strip()

    task = repository.create_task(title, user.id)

    invalidate_user_cache(user.id)

    return task


@app.post("/reset", status_code=204)
def reset_tasks(user=Depends(get_current_user)) -> None:
    repository.reset_tasks(user.id)

    keys = redis_client.keys(f"task:{user.id}:*")
    if keys:
        redis_client.delete(*keys)

    invalidate_user_cache(user.id)

    
@app.put("/tasks/{task_id}")
def update_task(task_id: int, data: dict = Body(...), user=Depends(get_current_user)) -> dict:
    if "title" not in data and "done" not in data:
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

    task = repository.update_task(task_id, data, user.id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    redis_client.delete(f"task:{user.id}:{task_id}")
    invalidate_user_cache(user.id)

    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, user=Depends(get_current_user)) -> None:
    try:
        repository.delete_task(task_id, user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    redis_client.delete(f"task:{user.id}:{task_id}")
    invalidate_user_cache(user.id)