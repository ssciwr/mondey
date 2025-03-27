# End-to-end testing

This directory contains test databases and static files for the backend to use when running the e2e tests.

## Running the e2e tests locally

- (if not already done) install the backend from the **mondey-backend** directory:
  - `pip install -e .[tests]`
- start the backend in the **e2e** directory (so that the backend uses the e2e test databases)
  - `mondey-backend`
- run the e2e tests in the **frontend** directory
  - `pnpm test:e2e:dev`
