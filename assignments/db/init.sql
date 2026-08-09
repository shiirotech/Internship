CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

INSERT INTO tasks (title, done, created_at, updated_at)
VALUES
    ('First task', False, NOW(), NOW()),
    ('Second task', False, NOW(), NOW()),
    ('Third task', False, NOW(), NOW());