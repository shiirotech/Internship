# Task API

A simple REST API for managing tasks, built with **FastAPI** as part of the **FlyRank AI Internship**.

The project demonstrates the implementation of CRUD (Create, Read, Update, Delete) operations with persistent storage using a SQLite database.

---

## Features

- Create a new task
- Retrieve all tasks
- Retrieve a task by its ID
- Update a task's title and/or completion status
- Delete a task
- Persistent data storage with SQLite
- Automatic task timestamps (`created_at`, `updated_at`)
- Filtering tasks by completion status
- Searching tasks by title
- Sorting tasks by title or ID
- Task statistics endpoint
- Reset database to example data
- Input validation with meaningful error responses

---

## Why SQLite?

SQLite was chosen because it is lightweight and requires zero additional setup. The entire database is stored in a single file, making it simple to use while still providing persistent storage that survives application restarts.

The database file is called `tasks.db`. It is created automatically when the application initializes the database. The file is usually added to `.gitignore`, so every clone of the repository starts with a fresh database generated locally.

---


## Installation

Clone the repository, navigate to the project directory, and create a virtual environment:

```bash
git clone https://github.com/shiirotech/Internship.git
cd Internship/assignment01_02

python -m venv .venv
```

Activate the virtual environment.

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the application

Start the development server:

```bash
fastapi dev app/main.py
```

The API will be available at:

```
http://127.0.0.1:8000
```

The interactive API documentation is available at:

```
http://127.0.0.1:8000/docs
```

![Swagger UI](/assignment01_02/screenshots/swagger_ui.png)

---

## Database

The application uses SQLite for persistent storage.

The database file:

```
tasks.db
```

is created automatically when the database initialization script is executed.

You can use **DB Browser** app to interact and observe the db itself.

![DB Browser](/assignment01_02/screenshots/db_browser.png)

## API Endpoints

- **GET /** – Returns general information about the API.

- **GET /health** – Returns the current health status of the application.

- **GET /tasks** – Returns a list of all tasks. Optional query parameters can be used to filter tasks by completion status (`done`), search tasks by title (`search`), and sort results by title or ID (`sort`).
Available sorting values:
`title`,
`-title`,
`id` and
`-id`.

- **GET /tasks/{task_id}** – Returns the task with the specified ID.

- **GET /stats** - Returns counts of: all tasks, finished and unfinished ones.

- **POST /tasks** – Creates a new task.

- **POST /reset** - Restores 3 example tasks and removes all newly added.

- **PUT /tasks/{task_id}** – Updates the title and/or completion status of an existing task.

- **DELETE /tasks/{task_id}** – Deletes the task with the specified ID.

---

## Example Request

Create a new task:

```http
POST /tasks
Content-Type: application/json

{
    "title": "New task"
}
```

Example response:

```json
{
    "id": 4,
    "title": "New task",
    "done": 0,
    "created_at": "2026-08-04T14:30:00",
    "updated_at": "2026-08-04T14:30:00"
}
```