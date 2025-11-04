# Development

Some information on how to locally build and serve the website if you would like to make changes to the code.
There are two ways to do this:

- docker
  - closer to production environment
  - but less convenient for development - you need to rebuild the image every time you make a change
- python/pnpm
  - further from production environment setup
  - but convenient for development - see changes immediately without having to rebuild or restart anything

## Run locally with docker

Requires docker and docker compose.

1. clone the repo:

```sh
git clone https://github.com/ssciwr/mondey.git
cd mondey
```

2. generate a local SSL cert/key pair:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes -subj '/CN=localhost'
```

3. define settings in a .env file in the mondey/mondey_backend folder. A sample .env.sample file is included in the root directory, which can be copied to the same directory to work as the .env for local development. You need to set values with these placeholders as described in that .env.sample file: (SECRETVALUE/APIVALUE). Note there are other env variables set with the defaults defined in settings.py, unless later overwritten in your mondey/mondey_backend/.env file, and a separate frontend .env file in mondey/frontend.

4. build and run the website locally in docker containers on your computer:

```sh
docker compose up --build -d
```

The website is then served at https://localhost/
(note that the SSL keys are self-signed keys and your browser will still warn about the site being insecure.)

Whenever you make a change to the code you need to re-run the above command to see the effect of your changes.

### Database

The default location for the postgres data is the `db` folder where you run the docker compose command.
To make an existing user with email address `you@address.com` into an admin, run the following commands:

Change the Docker database grep name to mondey-local-mondeydb-1 if you are running just docker DBs with local python.

```sh
docker exec -it $(docker ps | grep mondeydb-1 | awk '{print $1}') bash
psql -U postgres -d mondey
UPDATE user SET is_admin=true WHERE email='you@address.com';
```

Database migrations are done using Alembic, see [./mondey_backend/alembic/README.md](./mondey_backend/alembic/README.md) for more information.

## Run locally with Python and pnpm

Requires docker compose, Python and [pnpm](https://pnpm.io/installation#using-a-standalone-script)

1. clone the repo:

```sh
git clone https://github.com/ssciwr/mondey.git
cd mondey
```

2. from /mondey_backend, run the postgres mondey and user databases locally (this will start the postgres docker containers in detached mode and they will continue to run in the background):

```sh
docker compose -f docker-compose.localdatabases.yml up -d
```

Make sure that port `5432` && `5433` are available and check they set up to use those ports by running `docker ps -a`
They should be "Running" and show those port numbers.

3. install and run the backend development server:

```sh
cd mondey_backend
pip install -e .[tests]
cd ..
mondey-backend
```

Alternative option If you would like databases populated with fake research data and users, useful for testing the research database,
 run `mondey-backend` from the `/e2e` directory (that causes the databases to be populated with data). Proceed with step 4 in either case.
You need to carry out step 2 first either way. Step 2 sets up the database that the `mondey-backend` command will access.

4. install and run the frontend development server:

4.1: Copy /frontend/.env.sample to /frontend/.env - you most likely will not need to change it.

4.2: Run the frontend
```sh
cd frontend
pnpm install
pnpm run dev
```

The website is then served at http://localhost:5173/, and any changes to the frontend or backend code
will be reflected immediately in the browser.
