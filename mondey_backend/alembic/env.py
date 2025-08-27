import logging

from sqlmodel import SQLModel

from alembic import context
from mondey_backend.databases.mondey import engine as mondey_engine

# import all our models so that they are registered with SQLModel.metadata to allow alembic to autogenerate migrations
from mondey_backend.models.children import Child
from mondey_backend.models.milestones import AdminSettings
from mondey_backend.models.milestones import Language
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneAgeScore
from mondey_backend.models.milestones import MilestoneAgeScoreCollection
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneGroup
from mondey_backend.models.milestones import MilestoneGroupAgeScore
from mondey_backend.models.milestones import MilestoneGroupAgeScoreCollection
from mondey_backend.models.milestones import MilestoneGroupText
from mondey_backend.models.milestones import MilestoneText
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion
from mondey_backend.models.questions import UserQuestionText
from mondey_backend.models.research import ResearchGroup

# enable logging
logging.basicConfig(level=logging.INFO)

# run the migrations
with mondey_engine.connect() as connection:
    context.configure(connection=connection, target_metadata=SQLModel.metadata)
    with context.begin_transaction():
        context.run_migrations()
