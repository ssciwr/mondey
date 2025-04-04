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

## Data import SQL files

For now the data import is split into 2 SQL files: One for base SQL data (users, children, milestones and milestone groups)
`sqlite3 db/mondey.db < db/clearsqlimport.sql && mondey-backend`

The second one contains some fake milestone answering sessions and milestone answers (no question/answers):
`sqlite3 db/mondey.db < db/import_lots_of_milestone_answers.sql`
