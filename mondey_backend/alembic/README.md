# Database migrations

This directory contains the [Alembic](https://alembic.sqlalchemy.org/en/latest/) migrations for both the Mondey and users databases. Each revision contains separate `upgrade_mondey` and `upgrade_users` operations, and `alembic upgrade head` applies the revision to both databases.
Below are instructions for applying migrations manually, and for creating a new migration after making changes to the database models.

## Production

In production, migrations are automatically applied when the backend starts up in the backend Docker image.

## Development

To apply and create migrations when developing, you need to have both the mondey and the users databases
running and accessible (e.g. `docker compose -f docker-compose.localdatabases.yml up -d`),
and the `DATABASE_PASSWORD` environment variable needs to be defined, e.g. in a .env file in the mondey_backend directory.
Alembic reads this .env file from the directory you run it in, so run the commands below from the mondey_backend directory.

### Applying migrations

To apply the latest migrations to your database, run the following command from the mondey_backend directory:

```
alembic upgrade head
```

### Creating a migration

To create a new migration after making changes to the database models, run the following command in the mondey_backend directory:

```
alembic revision --autogenerate -m "Your migration message"
```

This will create a new migration file in the `alembic/versions` directory.

IMPORTANT: Always review the generated migration file to ensure it accurately reflects the changes you intend to make to the database schema!

You can then apply the migration locally using the `alembic upgrade head` command as described above.

Note: If you add a new model you will also need to add an import statement for it in the [env.py](env.py) file to ensure Alembic is aware of the new model when autogenerating migrations.

Migrations in this project are forward-only; downgrade operations are not generated or supported.
