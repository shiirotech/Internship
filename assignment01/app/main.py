from fastapi import FastAPI, HTTPException, Body
from datetime import datetime
import sqlite3

def get_timestamp():
    return datetime.now().replace(microsecond=0).isoformat()

app = FastAPI()


@app.get("/")
def read_root():
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
def read_status():
    return {"status": "ok"}

@app.get("/tasks")
def read_tasks(done: bool | None = None, search: str | None = None, sort: str | None = None):
    with sqlite3.connect("tasks.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        query = "SELECT * FROM tasks"
        conditions = []
        params = []

        if done is not None:
            conditions.append("done = ?")
            params.append(done)

        if search and search.strip():
            search = search.strip()
            conditions.append("title LIKE ?")
            params.append(f"%{search}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        if sort and sort.strip():
            sort = sort.strip().lower()
            if sort == "title":
                query += " ORDER BY title"
            elif sort == "-title":
                query += " ORDER BY title DESC"
            elif sort == "id":
                query += " ORDER BY id"
            elif sort == "-id":
                query += " ORDER BY id DESC"
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to sort using current parameter"
                )

        tasks = cur.execute(query, params).fetchall()

    return [dict(row) for row in tasks]

@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    with sqlite3.connect("tasks.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        task = cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return dict(task)

@app.get("/stats")
def read_stats():
    with sqlite3.connect("tasks.db") as con:
        cur = con.cursor()

        total = cur.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        count_done = cur.execute("SELECT COUNT(*) FROM tasks WHERE done = ?", (True,)).fetchone()[0]
        count_open = total - count_done

    return {
        "total": total,
        "done": count_done,
        "open": count_open
    }

@app.post("/tasks", status_code=201)
def create_task(data: dict = Body(...)):
    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        raise HTTPException(
            status_code=400,
            detail="No title has been specified"
        )

    title = title.strip()

    with sqlite3.connect("tasks.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        now = get_timestamp()

        cur.execute(
            """INSERT INTO tasks(title, done, created_at, updated_at)
            VALUES (?, ?, ?, ?)""", (title, False, now, now)
        )
        
        task_id = cur.lastrowid

        task = cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    return dict(task)

@app.post("/reset", status_code=201)
def reset_tasks():
    with sqlite3.connect("tasks.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute("DELETE FROM tasks")

        now = get_timestamp()

        data = [
            ("First task", False, now, now),
            ("Second task", False, now, now),
            ("Third task", False, now, now)
        ]
        
        cur.executemany(
            """INSERT INTO tasks(title, done, created_at, updated_at)
            VALUES (?, ?, ?, ?)""", data
        )

        tasks = cur.execute("SELECT * FROM tasks").fetchall()

    return [dict(task) for task in tasks]
    
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

    conditions = []
    params = []

    if "title" in data:
        title = data["title"]

        if not isinstance(title, str) or not title.strip():
            raise HTTPException(
                status_code=400,
                detail="The title should be a non-empty string"
            )
        
        conditions.append("title = ?")
        params.append(title.strip())

    if "done" in data:
        done = data["done"]

        if not isinstance(done, bool):
            raise HTTPException(
                status_code=400,
                detail="Done should be a boolean value (true or false)"
            )

        conditions.append("done = ?")
        params.append(done)

    now = get_timestamp()

    conditions.append("updated_at = ?")
    params.append(now)

    params.append(task_id)

    with sqlite3.connect("tasks.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        query = "UPDATE tasks SET " + ", ".join(conditions) + " WHERE id = ?"

        cur.execute(query, params)
    
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )

        task = cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    return dict(task)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with sqlite3.connect("tasks.db") as con:
        cur = con.cursor()

        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )