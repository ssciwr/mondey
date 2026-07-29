This folder contains SQL files to fill the temporary mondey and user databases used when running the backend for the end-to-end tests.

## importUsers.sql

Contains three users:

- user
  - email: user@mondey.de
  - password: `user`
- researcher
  - email: researcher@mondey.de
  - password: `researcher`
- admin
  - email: admin@mondey.de
  - password: `admin`

Note these passwords are shorter than the minimum length for a newly registered user - they are inserted
directly into the database and so bypass that check.

## importBaseMetadata.sql

- milestone groups and milestones, with their translated texts
- a few children with milestone answer sessions and answers

## importMilestoneAnswers.sql

- additional children, milestone answer sessions and milestone answers, to give the
  statistics and research data export something to work with
