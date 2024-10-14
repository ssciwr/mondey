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

3. build and run the website locally in docker containers on your computer:

```sh
docker compose up --build -d
```

The website is then served at https://localhost/
(note that the SSL keys are self-signed keys and your browser will still warn about the site being insecure.)

Whenever you make a change to the code you need to re-run the above command to see the effect of your changes.

### Database

The databases will by default be stored in a `db` folder
in the folder where you run the docker compose command.

### Make yourself an admin user

```
sudo sqlite3 docker_volume/predicTCR.db
sqlite> UPDATE user SET is_admin=true WHERE email='you@address.com';
sqlite> .quit
```

## Run locally with Python and pnpm

Requires Python and [pnpm](https://pnpm.io/installation#using-a-standalone-script)

1. clone the repo:

```sh
git clone https://github.com/ssciwr/mondey.git
cd mondey
```

2. install and run the backend development server:

```sh
cd mondey_backend
pip install .
cd ..
mondey-backend
```

3. install and run the frontend development server:

```sh
cd frontend
pnpm install
pnpm run dev
```

The website is then served at http://localhost:5173/.
