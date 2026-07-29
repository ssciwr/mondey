# Development

Some information on how to locally build and serve the website if you would like to make changes to the code.
There are two ways to do this:

- docker
  - closer to production environment
  - but less convenient for development - you need to rebuild the image every time you make a change
- python/pnpm
  - further from production environment setup
  - but convenient for development - see changes immediately without having to rebuild or restart anything

Requirements: docker and docker compose for both options, plus Python 3.13 and Node.js 24 with Corepack for the second.

## Configuration files

There are three separate `.env` files, and which ones you need depends on how you run the website:

| File | Read by | Needed for |
| --- | --- | --- |
| `.env` (repo root) | docker compose | running everything with docker |
| `mondey_backend/.env` | the backend and alembic | running the backend or migrations directly with Python |
| `frontend/.env` | vite | running the frontend dev server |

Sample files to copy and edit are provided: [mondey_backend/.env.dev.sample](mondey_backend/.env.dev.sample)
(and [mondey_backend/.env.prod.sample](mondey_backend/.env.prod.sample) for production) and
[frontend/.env.dev.sample](frontend/.env.dev.sample).
Replace the `SECRETVALUE` and `APIVALUE` placeholders as described in the sample file.
Note that `SECRET` must be at least 20 characters long or the backend will refuse to start.

Any setting not present in the `.env` file falls back to the default in
[settings.py](mondey_backend/src/mondey_backend/settings.py).

The backend reads `.env` from the directory you start it in, so `mondey_backend/.env` only takes effect
if you run `mondey-backend` and `alembic` from the `mondey_backend` directory.

## Run locally with docker

1. clone the repo:

```sh
git clone https://github.com/ssciwr/mondey.git
cd mondey
```

2. generate a local SSL cert/key pair in the repo root:

```sh
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes -subj '/CN=localhost'
```

3. copy `mondey_backend/.env.dev.sample` to `.env` **in the repo root** (docker compose only reads the
   `.env` next to the docker-compose.yml) and fill in the placeholder values.
   Set `MONDEY_HOST=localhost` so that the links in verification and password reset emails point at your
   local website.

4. build and run the website locally in docker containers on your computer:

```sh
docker compose up --build -d
```

The website is then served at https://localhost/
(note that the SSL keys are self-signed keys and your browser will still warn about the site being insecure.)

Whenever you make a change to the code you need to re-run the above command to see the effect of your changes.

## Run locally with Python and pnpm

1. clone the repo:

```sh
git clone https://github.com/ssciwr/mondey.git
cd mondey
```

2. copy `mondey_backend/.env.dev.sample` to `mondey_backend/.env` and fill in the placeholder values,
   and copy `frontend/.env.dev.sample` to `frontend/.env` (you most likely will not need to change it).

3. start the mondey and users postgres databases in the background:

```sh
cd mondey_backend
docker compose -f docker-compose.localdatabases.yml up -d
```

This uses the `DATABASE_PASSWORD` from `mondey_backend/.env`, so it must match what the backend uses.
Ports `5432` (mondey) and `5433` (users) need to be free; check with `docker ps` that both containers are running.

4. install and run the backend development server, from the `mondey_backend` directory:

```sh
pip install -e .[tests]
mondey-backend
```

5. install and run the frontend development server:

```sh
cd ../frontend
corepack enable
pnpm install
pnpm run dev
```

The website is then served at http://localhost:5173/, and any changes to the frontend or backend code
will be reflected immediately in the browser.

### Running the backend with test data

If you would like databases populated with fake research data and users, which is useful for testing the
research and statistics features, run `mondey-backend` from the `e2e` directory instead:

```sh
cd e2e
mondey-backend
```

This uses [e2e/.env](e2e/.env), which sets the database hosts to empty. That makes the backend create
**temporary sqlite databases** which are populated from the SQL files in [e2e/sql](e2e/sql) and deleted
again when the backend stops. The postgres containers from step 3 are not used and don't need to be running.
The test accounts this creates are listed in [e2e/sql/README.md](e2e/sql/README.md).

## Database

The default location for the postgres data is the `db` folder where you run the docker compose command.

To make an existing user with email address `you@address.com` into an admin, modify the **users** database:

```sh
docker exec -it $(docker ps | grep usersdb-1 | awk '{print $1}') bash
psql -U postgres -d users
UPDATE "user" SET is_superuser = true WHERE email = 'you@address.com';
```

This only needs to be done once - that user can then give other users admin rights from the admin interface.

Database migrations are done using Alembic, and are applied automatically when the backend starts in docker.
If you change the database models you need to generate a migration for the change - see
[./mondey_backend/alembic/README.md](./mondey_backend/alembic/README.md) for more information.

## Tests

Backend unit tests, from the `mondey_backend` directory (these use in-memory sqlite databases, so nothing
needs to be running):

```sh
pytest
```

Frontend unit tests and component (ui) tests, from the `frontend` directory:

```sh
pnpm test:unit
pnpm test:ui        # or pnpm test:ui:dev to run them interactively
```

End-to-end tests, which need a backend with the test data running: start `mondey-backend` from the `e2e`
directory as described above, then from the `frontend` directory:

```sh
pnpm build
pnpm test:e2e       # or pnpm test:e2e:dev to run them interactively
```

Type checking of the frontend code:

```sh
pnpm run check
```

## Code formatting and linting

Formatting and linting of both the Python and the frontend code is configured in
[.pre-commit-config.yaml](.pre-commit-config.yaml) and is also run by the CI.
To run it locally, install [prek](https://github.com/j178/prek) and install the git hooks:

```sh
pip install prek
prek install
```

The hooks then run on the files you have changed each time you commit.
To run them on all files: `prek run --all-files`

## Generated API client

The frontend talks to the backend using a typed client that is generated from the backend OpenAPI schema,
so `mondey_backend/openapi.json` and `frontend/src/lib/client` should not be edited by hand -
the CI regenerates them on every pull request and commits any changes.

To regenerate them yourself after changing a backend endpoint or model:

```sh
cd mondey_backend && mondey-export-openapi-json
cd ../frontend && pnpm openapi-ts
```
