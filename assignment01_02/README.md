# Task API

A simple REST API for managing tasks, built with **FastAPI** as part of the **FlyRank AI Internship**.

The project demonstrates the implementation of CRUD (Create, Read, Update, Delete) operations using an in-memory list of tasks.

---

## Features

- Create a new task
- Retrieve all tasks
- Retrieve a task by its ID
- Update a task's title and/or completion status
- Delete a task
- Input validation with meaningful error responses

---

## Installation

Clone the repository, navigate to the project directory, and create a virtual environment:

```bash
git clone https://github.com/shiirotech/Internship.git
cd Internship/assignment01

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

---

## API Endpoints

- **GET /** – Returns general information about the API.

- **GET /health** – Returns the current health status of the application.

- **GET /tasks** – Returns a list of all tasks or only those specified in query parameters.

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
    "done": false
}
```