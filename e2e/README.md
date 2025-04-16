# End-to-end testing

This directory contains SQL data and static files for the backend to use when running the e2e tests.

## Running the e2e tests locally

- (if not already done) install the backend from the **mondey-backend** directory:
  - `pip install -e .[tests]`
- start the backend in the **e2e** directory with an empty database path and the e2e test sql files:
  - `RELOAD=false SMTP_HOST="" DATABASE_PATH="" E2E_TEST_USER_SQL_FILES="sql/importUsers.sql" E2E_TEST_MONDEY_SQL_FILES="sql/importBaseMetadata.sql;sql/importMilestoneAnswers.sql" mondey-backend`
- run the e2e tests in the **frontend** directory
  - `pnpm test:e2e:dev`

Each time the backend is started with the above command the in-memory databases will get regenerated using the e2e test data from the sql files.
