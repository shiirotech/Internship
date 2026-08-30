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
- Reset the current user's tasks
- Input validation
- User authentication with Supabase
- User-specific tasks and data isolation
- Protected endpoints using JWT access tokens
- Access token refresh using refresh tokens
- User logout
- Swagger UI authentication with Bearer tokens

---

## Authentication

The API uses **Supabase Auth** for user authentication.

Before using the authentication endpoints, create a new Supabase project.

![Supabase](/assignments/screenshots/supabase.png)

In the Supabase dashboard, go to `Authentication` → `Providers` → `Email` and disable `Confirm email`. This allows users to sign up and immediately log in without email verification.

![Disable email](/assignments/screenshots/disable_email.png)

With Supabase, users can:

- Sign up with an email and password
- Log in to receive an access token and refresh token
- Use the access token to access protected endpoints
- Refresh an expired access token using the refresh token
- Log out from the current session

Protected endpoints require an HTTP Bearer token:

```http
Authorization: Bearer <access_token>
```

Swagger UI provides an Authorize button that allows an access token to be entered once and reused for protected endpoints. Enter the access token as a Bearer token, then use Try it out to make authenticated requests.

![FastAPI authorize button](/assignments/screenshots/authorize.png)

---

## Why PostgreSQL?

PostgreSQL was chosen because it is a powerful and reliable relational database suitable for applications that may grow beyond a simple local setup. Unlike SQLite, PostgreSQL runs as a separate database server and supports multiple concurrent connections while providing strong data integrity and transaction features.

---

## Environment variables

Create a `.env` file containing:

```env
DATABASE_URL=postgres://postgres:your_password@127.0.0.1:5432/tasks
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=tasks
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=sb_publishable_xxxxx
```

---

## Installation (using Docker Desktop)

Clone the repository, navigate to the project directory and start the application (make sure Docker Desktop is running):

```bash
git clone https://github.com/shiirotech/Internship.git
cd Internship/assignments

docker compose up --build
```

To see the documentation, visit:

```
http://127.0.0.1:8000/docs
```

For any subsequent runs use:

```bash
docker compose up
```

When running with Docker Compose, the `DATABASE_URL` is configured automatically using the PostgreSQL service name `db`. The `.env` value using `127.0.0.1` is intended for manual/local execution only.

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

`DATABASE_URL=postgres://your_user:your_password@127.0.0.1:5432/your_db_name`

Adjust the username, password, and database name if your local PostgreSQL configuration differs.

---

## Running the application

Start the server (required for manual installation only):

```bash
fastapi run app/main.py
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

The database schema is created automatically from `db/init.sql` when the database is initialized for the first time.

Tasks are associated with a specific authenticated user through the `user_id` column. Each user's task operations are restricted to their own tasks.

You can use **pgAdmin** or another PostgreSQL client to connect to and interact with the database.

![pgAdmin](/assignments/screenshots/pgAdmin.png)

---

## API Endpoints

- **GET /** – Returns general information about the API.

- **GET /health** – Returns the current health status of the application.

The following task-related endpoints are user-specific and require authentication:

- **GET /tasks** – Returns a list of all user tasks. Optional query parameters can be used to filter tasks by completion status (`done`), search tasks by title (`search`), and sort results by title or ID (`sort`).
Available sorting values:
`title`,
`-title`,
`id` and
`-id`.

- **GET /tasks/{task_id}** – Returns the user task with the specified ID.

- **GET /stats** - Returns counts of: all user tasks, finished and unfinished ones.

- **POST /tasks** – Creates a new task for the current user.

- **POST /reset** - Deletes all tasks for the current user.

- **PUT /tasks/{task_id}** – Updates the title and/or completion status of an existing user task.

- **DELETE /tasks/{task_id}** – Deletes the user task with the specified ID.

### Authentication

- **POST /auth/signup** – Creates a new user account using an email and password.

- **POST /auth/login** – Authenticates a user and returns an access token and refresh token.

- **POST /auth/refresh** – Uses a refresh token to obtain a new access token without requiring the user to log in again.

- **POST /auth/logout** – Logs out the authenticated user. Requires a valid access token.

### Protected Endpoints

The following endpoints require authentication:

- **GET /protected/profile** – Returns full information about the authenticated user.

- **GET /protected/dashboard** – Returns a dashboard containing some brief information about the authenticated user.

- **GET /protected/admin** – Demonstrates role-like authorization by allowing access only to the configured administrator.

All task and statistics endpoints also require authentication. Users can only access their own tasks and statistics.

---

## Example Request

Create a new task:

```http
POST /tasks
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "title": "New task"
}
```

Example response:

```json
{
    "id": 4,
    "user_id": "<user_uuid>",
    "title": "New task",
    "done": false,
    "created_at": "2026-08-04T14:30:00Z",
    "updated_at": "2026-08-04T14:30:00Z"
}
```