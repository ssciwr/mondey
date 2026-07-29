# MONDEY backend

The MONDEY backend is a FastAPI application that provides a RESTful API for the MONDEY project.

See [DEVELOPMENT.md](../DEVELOPMENT.md) for the full local development setup.

## Installation

Requires Python 3.13.

```bash
pip install -e .[tests]
```

## Use

To start a local development server, from this directory:

```bash
mondey-backend
```

This will start the backend on [http://localhost:8000](http://localhost:8000),
which includes a redoc UI for exploring the API and a swagger UI for interacting with it:

- [http://localhost:8000/redoc](http://localhost:8000/redoc)
- [http://localhost:8000/docs](http://localhost:8000/docs)

This needs the mondey and users postgres databases to be running, which you can start with:

```bash
docker compose -f docker-compose.localdatabases.yml up -d
```

## Configuration

The backend can be configured using environment variables, which can be set in a `.env` file in the
directory you start the backend from. There is a sample for both development
([.env.dev.sample](.env.dev.sample)) and production ([.env.prod.sample](.env.prod.sample)) here to copy and edit.
Settings that are not set fall back to the defaults in
[settings.py](src/mondey_backend/settings.py).

If `DATABASE_HOST_MONDEYDB` and `DATABASE_HOST_USERSDB` are empty the backend uses temporary sqlite
databases instead, which are deleted when it stops. This is what the tests and the end-to-end test setup use.

## Admin user

The first admin user can only be created by modifying the users database directly.
After you have registered a user, you can promote them to an admin user with e.g.:

```bash
docker exec -it $(docker ps | grep usersdb-1 | awk '{print $1}') bash
psql -U postgres -d users
UPDATE "user" SET is_superuser = true WHERE email = 'youremail@yourdomain.com';
```

## Database migrations

Schema changes are managed with Alembic, see [alembic/README.md](alembic/README.md).

## Tests

```bash
pytest
```

These use in-memory sqlite databases, so the postgres containers don't need to be running.
