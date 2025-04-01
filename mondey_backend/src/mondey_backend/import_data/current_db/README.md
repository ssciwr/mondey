# Database set up

There are 3 database directories during normal operation of this import script.

`/db`: `mondey_backend/db/mondey.db and mondey_backend/db/users.db`: These are the live databases.
*the script does not change these*

`/src/mondey_backend/import_data/current_db`: `/src/mondey_backend/import_data/current_db/current_mondey.db` and `/src/mondey_backend/import_data/current_db/current_users.db`
*These act as a cordon sanitare from overwriting the real existing current milestones.
You should place a _copy_ of the live databases into these two files, before running the script*

`/src/mondey_backend/import_data/db`: `/src/mondey_backend/import_data/db/mondey.db` and `/src/mondey_backend/import_data/db/mondey.db`: Legacy import test databases
*these were used in the original version*
