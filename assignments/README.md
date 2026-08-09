# Task API

A simple REST API for managing tasks, built with **FastAPI** as part of the **FlyRank AI Internship**.

The project demonstrates the implementation of CRUD (Create, Read, Update, Delete) operations with persistent storage using a PostgreSQL database.

---

## Features

- Create a new task
- Retrieve all tasks
- Retrieve a task by its ID
- Update a task's title and/or completion status
- Delete a task
- Persistent data storage with PostgreSQL
- Automatic task timestamps (`created_at`, `updated_at`)
- Filtering tasks by completion status
- Searching tasks by title
- Sorting tasks by title or ID
- Task statistics endpoint
- Reset database to example data
- Input validation with meaningful error responses

---

## Why PostgreSQL?

PostgreSQL was chosen because it is a powerful and reliable relational database suitable for applications that may grow beyond a simple local setup. Unlike SQLite, PostgreSQL runs as a separate database server and supports multiple concurrent connections while providing strong data integrity and transaction features.

---

## Installation (using Docker Desktop)

Clone the repository, navigate to the project directory and start the application (make sure Docker Desktop is running):

```bash
git clone https://github.com/shiirotech/Internship.git
cd Internship/assignments

docker compose up --build
```

For any subsequent runs use:

```bash
docker compose up
```

---

## Installation (manual)

Clone the repository, navigate to the project directory, and create a virtual environment:

```bash
git clone https://github.com/shiirotech/Internship.git
cd Internship/assignments

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

### PostgreSQL

Make sure PostgreSQL 17 is running locally on port `5432`.

Create a database named `tasks` and initialize its schema using `db/init.sql`.

The connection string in `.env` should point to the local PostgreSQL instance:

`DATABASE_URL=postgres://postgres:<password>@127.0.0.1:5432/tasks`

Adjust the username, password, and database name if your local PostgreSQL configuration differs.

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

![Swagger UI](/assignments/screenshots/swagger_ui.png)

---

## Database

The application uses PostgreSQL for persistent storage.

When using Docker Compose, PostgreSQL runs in a Docker container, with its data stored in a persistent Docker volume called `taskdata`.

The database schema and initial seed data are created automatically from `db/init.sql` when the database is initialized for the first time.

You can use **pgAdmin** or another PostgreSQL client to connect to and interact with the database.

![pgAdmin](/assignments/screenshots/pgAdmin.png)

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
    "done": false,
    "created_at": "2026-08-04T14:30:00",
    "updated_at": "2026-08-04T14:30:00"
}
```