This folder contains a pre-filled users database, and SQL files to fill the mondey database - to be used when running the end-to-end tests.

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

This database is generated when running the e2e tests (and should not be committed to the git repo)

## Data import SQL files

- importBaseMetadata.sql: base SQL data (users, children, milestones and milestone groups)
- importMilestoneAnswers.sql: milestone answering sessions and milestone answers (no question/answers)
