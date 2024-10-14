# MONDEY backend

The MONDEY backend is a FastAPI application that provides a RESTful API for the MONDEY project.

## Installation

```bash
pip install -e .[tests]
```

## Use

To start a local development server:

```bash
mondey-backend
```

This will start the backend on [http://localhost:8000](http://localhost:8000),
which includes a redoc UI for exploring the API and a swagger UI for interacting with it:

- [http://localhost:8000/redoc](http://localhost:8000/redoc)
- [http://localhost:8000/docs](http://localhost:8000/docs)

## Admin user

The first admin user can only be created by modifying the database directly.
After you have registered a user using the swagger UI, you can promote them to an admin user with e.g.:

```bash
sqlite3 db/users.db
sqlite> UPDATE user SET is_superuser = 1 WHERE email = 'youremail@yourdomain.com';
sqlite> .quit
```

## Configuration

The backend can be configured using environment variables,
which can be set in a `.env` file in the working directory where you start the backend.

## Tests

```bash
pytest
```
