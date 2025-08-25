# [MONDEY](https://mondey.de/)
[![ci](https://github.com/ssciwr/mondey/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/mondey/actions/workflows/ci.yml)
[![sonar](https://sonarcloud.io/api/project_badges/measure?project=ssciwr_mondey&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ssciwr_mondey)
[![codecov](https://codecov.io/gh/ssciwr/mondey/graph/badge.svg?token=1YBO3KUDAR)](https://codecov.io/gh/ssciwr/mondey)

The source code for the MONDEY: Milestones of Normal Development in Early Years website.

### Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for instructions on how to run the website locally.

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on how to deploy the website to a server.

### Docker compose
The docker compose in the root folder runs all of the services together. An .env file needs to be present.

## How Mondey runs
Each instance of Mondey can run by running the docker compose up with that env file, and all the containers should
then interconnect. Some functionality, like emails being authenticated, requires more work, while HTTPS for the
frontend requires a domain name to be pointed via A record at the VM/IP address which points to the VM/server.

## Parts of docker compose
The major parts of the docker compose are:
- The Frontend (An Nginx proxy which serves a vite Svelte web application)
- The Backend API (Which gets requests from the Frontend)
- Two database postgres containers (Using "Users" for authentication with FastAPI implementation, and "Mondey" for
the domain-specific data)

Additional containers take on admin roles:
- The email server sends emails
- Watchtower updates the running docker images
- Back up services take Backups

· Important note: Changes to database structure need to be coordinated with updates/updating the docker containers,
to ensure the backend can still run with the changed data format (e.g. by running a migration .SQL file).

### Licensing

The source code in this repository was developed by the [Scientific Software Center](https://ssc.uni-heidelberg.de)
and is distributed under [AGPL-3.0-or-later](LICENSE).

All content in the website deployed at [mondey.de](https://mondey.de) is copyright © 2025 Psychologisches Institut Heidelberg.
