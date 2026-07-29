# [MONDEY](https://mondey.de/)
[![ci](https://github.com/ssciwr/mondey/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/mondey/actions/workflows/ci.yml)
[![sonar](https://sonarcloud.io/api/project_badges/measure?project=ssciwr_mondey&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ssciwr_mondey)
[![codecov](https://codecov.io/gh/ssciwr/mondey/graph/badge.svg?token=1YBO3KUDAR)](https://codecov.io/gh/ssciwr/mondey)

The source code for the MONDEY: Milestones of Normal Development in Early Years website.

### Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for instructions on how to run the website locally.

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on how to deploy the website to a server.

### How MONDEY runs

The [docker-compose.yml](docker-compose.yml) in the root folder runs all of the services together.
It requires a `.env` file in the same folder - see [DEPLOYMENT.md](DEPLOYMENT.md) for the settings it needs.

The main services are:

- **frontend** - an nginx server which serves the built Svelte web application and proxies `/api` to the backend
- **backend** - the FastAPI application
- **mondeydb** - postgres database with the domain-specific data
- **usersdb** - postgres database with the user accounts used by fastapi-users for authentication

Supporting services:

- **email** - a send-only postfix server
- **mondeydb-backup** / **usersdb-backup** - daily backups of each database
- **watchtower** - pulls and restarts updated docker images each night

HTTPS for the frontend requires a domain name pointed via an A record at the server, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Licensing

The source code in this repository was developed by the [Scientific Software Center](https://ssc.uni-heidelberg.de)
and is distributed under [AGPL-3.0-or-later](LICENSE).

All content in the website deployed at [mondey.de](https://mondey.de) is copyright © 2025 Psychologisches Institut Heidelberg.
