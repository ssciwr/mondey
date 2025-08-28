import logging

from sqlmodel import SQLModel

from alembic import context
from mondey_backend.databases.mondey import engine as mondey_engine

# import all our models so that they are registered with SQLModel.metadata to allow alembic to autogenerate migrations
from mondey_backend.models.children import *
from mondey_backend.models.milestones import *
from mondey_backend.models.questions import *
from mondey_backend.models.research import *

# enable logging
logging.basicConfig(level=logging.INFO)

# run the migrations
with mondey_engine.connect() as connection:
    context.configure(connection=connection, target_metadata=SQLModel.metadata)
    with context.begin_transaction():
        context.run_migrations()
