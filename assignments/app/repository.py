from dotenv import load_dotenv
import os
import psycopg
from psycopg.rows import dict_row
from datetime import datetime, date


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_timestamp() -> datetime:
    return datetime.now().replace(microsecond=0)


class PostgresTaskRepository:
    def db_status(self) -> str:
        try:
            with psycopg.connect(DATABASE_URL) as con:
                with con.cursor() as cur:
                    cur.execute("SELECT 1")
                    return "ok"
        except psycopg.OperationalError:
            return "bad"


    def read_tasks(
        self,
        user_id: str,
        done: bool | None = None,
        search: str | None = None,
        sort: str | None = None,
        priority: str | None = None,
        due_date: date | None = None
    ) -> list[dict]:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:
        
                query = "SELECT * FROM tasks"
                conditions = []
                params = []

                conditions.append("user_id = %s")
                params.append(user_id)
        
                if done is not None:
                    conditions.append("done = %s")
                    params.append(done)
        
                if search and search.strip():
                    search = search.strip()
                    conditions.append("title ILIKE %s")
                    params.append(f"%{search}%")

                if priority is not None:
                    conditions.append("task_priority = %s")
                    params.append(priority)

                if due_date is not None:
                    conditions.append("due_date = %s")
                    params.append(due_date)
        
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
                        raise ValueError(
                            "Unable to sort using current parameter"
                        )
        
                rows = cur.execute(query, params).fetchall()
        
        return rows


    def read_task(self, task_id: int, user_id: str) -> dict | None:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:
        
                row = cur.execute(
                    "SELECT * FROM tasks WHERE user_id = %s AND id = %s",
                    (user_id, task_id)
                ).fetchone()
        
        return row


    def read_stats(self, user_id: str) -> dict:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:

                total = cur.execute(
                    "SELECT COUNT(*) FROM tasks WHERE user_id = %s",
                    (user_id,)
                ).fetchone()["count"]

                count_done = cur.execute(
                    "SELECT COUNT(*) FROM tasks WHERE user_id = %s AND done = %s",
                    (user_id, True)
                ).fetchone()["count"]

                count_open = total - count_done

                high_priority = cur.execute(
                    "SELECT COUNT(*) FROM tasks WHERE user_id = %s AND task_priority = %s",
                    (user_id, "high")
                ).fetchone()["count"]

                med_priority = cur.execute(
                    "SELECT COUNT(*) FROM tasks WHERE user_id = %s AND task_priority = %s",
                    (user_id, "medium")
                ).fetchone()["count"]

                low_priority = total - high_priority - med_priority

                no_deadline = cur.execute(
                    "SELECT COUNT(*) FROM tasks WHERE user_id = %s AND due_date IS NULL",
                    (user_id,)
                ).fetchone()["count"]

                has_deadline = total - no_deadline

        return {
            "total": total,
            "done": count_done,
            "open": count_open,
            "high priority": high_priority,
            "medium priority": med_priority,
            "low priority": low_priority,
            "with deadline": has_deadline,
            "no deadline": no_deadline
        }


    def create_task(
        self,
        title: str,
        priority: str,
        due_date: date | None,
        user_id: str
    ) -> dict:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:

                now = get_timestamp()

                cur.execute(
                    """
                    INSERT INTO tasks(user_id, title, done, task_priority, due_date, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (user_id, title, False, priority, due_date, now, now)
                )

                row = cur.fetchone()

        return row


    def reset_tasks(self, user_id: str) -> None:
        with psycopg.connect(DATABASE_URL) as con:
            with con.cursor() as cur:

                cur.execute("DELETE FROM tasks WHERE user_id = %s", (user_id,))


    def update_task(self, task_id: int, data: dict, user_id: str) -> dict | None:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row) as con:
            with con.cursor() as cur:

                updates = []
                params = []

                if "title" in data:
                    updates.append("title = %s")
                    params.append(data["title"])

                if "done" in data:
                    updates.append("done = %s")
                    params.append(data["done"])

                if "priority" in data:
                    updates.append("task_priority = %s")
                    params.append(data["priority"])

                if "due_date" in data:
                    updates.append("due_date = %s")
                    params.append(data["due_date"])

                now = get_timestamp()

                updates.append("updated_at = %s")
                params.extend([now, user_id, task_id])

                query = (
                    "UPDATE tasks SET " +
                    ", ".join(updates) +
                    " WHERE user_id = %s AND id = %s"
                    " RETURNING *"
                )
                
                cur.execute(query, params)
        
                row = cur.fetchone()
        
        return row


    def delete_task(self, task_id: int, user_id: str) -> None:
        with psycopg.connect(DATABASE_URL) as con:
            with con.cursor() as cur:

                cur.execute("DELETE FROM tasks WHERE user_id = %s AND id = %s", (user_id, task_id))

                if cur.rowcount == 0:
                    raise ValueError(
                        f"Task {task_id} not found"
                    )