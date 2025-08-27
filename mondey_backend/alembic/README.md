# Database migrations

This directory contains the [Alembic](https://alembic.sqlalchemy.org/en/latest/) migrations for the Mondey database.
Below are instructions for applying migrations manually, and for creating a new migration after making changes to the database models.

## Production

In production, migrations are automatically applied when the backend starts up in the backend Docker image.

## Development

To apply and create migrations when developing, you need to have the mondey database running and accessible,
as well as making sure the `DATABASE_PASSWORD` environment variable is defined, e.g. in a .env file in the mondey_backend directory.

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

### Reverting a migration

To revert the last applied migration in your database, you can use the following command:

```
alembic downgrade -1
```
