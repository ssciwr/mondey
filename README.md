# [MONDEY](https://mondey.lkeegan.dev/)
[![run tests](https://github.com/ssciwr/mondey/actions/workflows/ci.yml/badge.svg)](https://github.com/ssciwr/mondey/actions/workflows/ci.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ssciwr_mondey&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ssciwr_mondey)
[![codecov](https://codecov.io/gh/ssciwr/mondey/graph/badge.svg?token=1YBO3KUDAR)](https://codecov.io/gh/ssciwr/mondey)

The source code for the MONDEY website. This is currently under development!

## Current status

The website is temporarily hosted on a heicloud VM during development:

### User interface

This is the website that the end user would interact with (functionality is currently incomplete):

- [Mondey website](https://mondey.lkeegan.dev/)

Until more functionality is added to the main site above, there are also some stand-alone previews of individual components:

- [Milestone component](https://mondey.lkeegan.dev/milestone)
- [MilestoneGroup component](https://mondey.lkeegan.dev/milestonegroup)

### Admin interface

This is the interface that admins would use to edit the contents of the website:

- [Mondey admin interface](https://mondey.lkeegan.dev/admin)

### Developer interface

These API interfaces are only temporarily public for convenience during development, in production these will not be public:

- [API documentation](https://mondey.lkeegan.dev/api/redoc)
- [Swagger UI to interact with API](https://mondey.lkeegan.dev/api/docs)

### Licensing

The source code in this repository is distributed under [AGPL-3.0-or-later](LICENSE).

## To run from local development:
From this directory: `docker-compose -f docker-compose.dev.yml up --build`

This will build a local set of containers. The frontend container will be mounting your code volume and running the command
`pnpm run dev`, so via hot reload it will automatically trigger reacting to code changes and updated the frontend you access rather than need
to rebuild the frontend container each time.
