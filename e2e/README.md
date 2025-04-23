# End-to-end testing

This directory contains SQL data and static files for the backend to use when running the e2e tests.

## Running the e2e tests locally

- (if not already done) install the backend from the **mondey-backend** directory:
  - `pip install -e .[tests]`
- start the backend in the **e2e** directory (it will use temporary databases populated with the e2e test sql data - see the .env file):
  - `mondey-backend`
- run the e2e tests in the **frontend** directory
  - `pnpm test:e2e:dev`

Each time the backend is started with the above command new temporary databases will be created and populated with the data from the SQL files.
