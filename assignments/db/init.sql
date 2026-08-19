CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

INSERT INTO tasks (title, done, created_at, updated_at)
VALUES
    ('First task', False, CURRENT_TIMESTAMP(0), CURRENT_TIMESTAMP(0)),
    ('Second task', False, CURRENT_TIMESTAMP(0), CURRENT_TIMESTAMP(0)),
    ('Third task', False, CURRENT_TIMESTAMP(0), CURRENT_TIMESTAMP(0));