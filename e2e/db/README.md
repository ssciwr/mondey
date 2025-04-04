This folder contains the pre-filled backend databases to be used when running the end-to-end tests.

## users.db

This database contains three users:

- user
  - email: user@mondey.de
  - password: `user`
- researcher
  - email: researcher@mondey.de
  - password: `researcher`
- admin
  - email: admin@mondey.de
  - password: `admin`

## mondey.db

This database contains

- child of user with name "userChild1" born 2024/12
-
## When running end to end tests:
Use this command to run the test database, then fill it with SQL (we do this because .db is obscure), then run the
backend - make sure to do this from the /e2e/ directory, not the normal backend directory!

`sqlite3 db/mondey.db < db/clearsqlimport.sql && mondey-backend`
(then in another tab you can run the Playwright/UI tests)

Don't commit changes to e2e/db/mondey.db, only the import script.
