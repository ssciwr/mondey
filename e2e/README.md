# End-to-end testing

This directory contains test database, SQL and static files for the backend to use when running the e2e tests.

## Running the e2e tests locally

- (if not already done) install the backend from the **mondey-backend** directory:
  - `pip install -e .[tests]`
- start the backend in the **e2e** directory specifying the e2e test sql files to use:
  - `rm -f db/mondey.bd && RELOAD=false SMTP_HOST="" E2E_TEST_SQL_FILES="db/importBaseMetadata.sql;db/importMilestoneAnswers.sql" mondey-backend`
- run the e2e tests in the **frontend** directory
  - `pnpm test:e2e:dev`

If you stop and restart the backend using the above command then the mondey.db database will get regenerated with the e2e test data.
