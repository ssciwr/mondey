"""
ImportManager class for handling all data import operations.

This class centralizes the import functionality that was previously spread across
multiple scripts, providing a more maintainable and cohesive approach.
"""

from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd
from fastapi_users.db import SQLAlchemyUserDatabase
from fuzzywuzzy import fuzz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session
from sqlmodel import select

from mondey_backend.import_data.manager.data_manager import DataManager
from mondey_backend.import_data.postprocessing_corrections.convert_fruhgeboren_data_into_two_questions import (
    parse_weeks,
)
from mondey_backend.import_data.postprocessing_corrections.run_postprocess_corrections import (
    run_postprocessing_corrections,
)
from mondey_backend.models.children import Child
from mondey_backend.models.milestones import Language
from mondey_backend.models.milestones import Milestone
from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import MilestoneText
from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import ChildQuestionText
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion
from mondey_backend.models.questions import UserQuestionText
from mondey_backend.models.users import User
from mondey_backend.models.users import UserCreate

logger = logging.getLogger(__name__)


class ImportManager:
    """
    Centralized manager for all data import operations.

    This class handles:
    1. Loading and parsing CSV data
    2. Creating and managing database connections
    3. Importing milestones metadata
    4. Importing children with milestone data
    5. Importing question/answer data
    6. Aligning additional data with existing data
    """

    def __init__(self, debug: bool = False):
        """
        Initialize the ImportManager.

        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        self._setup_logging()

        # Initialize DataManager
        self.data_manager = DataManager(debug=debug)

        # Mappings
        self.child_parent_map = {}
        self.milestone_mapping = {}
        self.milestone_group_mapping = {}

        # Hardcoded mappings from the original code
        self.birth_year_mapping = {
            9: 2025,
            1: 2024,
            2: 2023,
            3: 2022,
            4: 2021,
            5: 2020,
            6: 2019,
            7: 2018,
            8: 2017,
        }

        self.birth_month_mapping = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            7: 7,
            8: 8,
            9: 9,
            10: 10,
            11: 11,
            12: 12,
        }

        # Milestone group mappings
        self.milestone_group_id_map = {
            "GM": "2",  # Grobmotorik
            "HM": "1",  # Handmotorik
            "SE": "5",  # Soziale Entwicklung
            "SP": "4",  # Sprache
            "SV": "7",  # Schulische Vorläuferfertigkeiten
            "UZ": "6",  # Umgang mit inneren Zuständen
            "DE": "3",  # Denken
        }

        # Hardcoded mappings from hardcoded_additional_data_answer_saving.py
        self.age_of_birth_questions = ["Geburtsjahr", "Geburtsmonat"]
        self.eltern_questions = ["Mütter", "Väter", "Eltern", "Andere Verwandte"]
        self.eltern_question_variables = ["FP01", "FP02", "FP03", "FP04"]
        self.specific_fruhgeboren_week_questions = [
            "Fruhgeboren [01]",
            "Fruhgeboren? [01]",
        ]
        self.fruhbgeboren_and_teringeboren_variables = ["FK03", "FK04_01"]
        self.fruhgeboren_questions = [
            *self.specific_fruhgeboren_week_questions,
            "Termingeboren",
        ]
        self.younger_older_sibling_questions = [
            "Jüngere Geschwister",
            "Ältere Geschwister",
        ]
        self.younger_older_sibling_variables = ["FK08_01", "FK08_02"]

        self.andere_diagnosed_question = "Andere Diagnosen: [01]"
        self.child_age_questions_labels = ["FK01", "FK02"]
        self.variables_to_ignore_with_reasons = {
            "FK08": "Needless younger sibling related yes/no question",
            "FK08_03": "Needless younger sibling related question",
        }

        self.gesundheit_variables = [
            "FK05_01",
            "FK05_02",
            "FK05_03",
            "FK05_04",
            "FK05_05",
            "FK05_06",
            "FK05_07",
            "FK06_01",
        ]

        self.andere_diagnosen_other_question_variable = "FK06_01"
        self.nationality_other_question_variable = "FE03_01"
        self.muttersprache_other_question_variable = "FE05_01"
        self.additional_answer_variables = [
            self.andere_diagnosen_other_question_variable,
            self.nationality_other_question_variable,
            self.muttersprache_other_question_variable,
        ]

        self.relevant_child_variables = [
            *self.fruhbgeboren_and_teringeboren_variables,
            *self.gesundheit_variables,
            self.andere_diagnosen_other_question_variable,
            "FK07",
            "FK11",
            "FK12",
            *self.younger_older_sibling_variables,
        ]

        self.relevant_user_variables = [
            *self.eltern_question_variables,
            "FE08",
            "FE07",
            "FE06",
            "FE04",
            self.muttersprache_other_question_variable,
            self.nationality_other_question_variable,
        ]

        self.all_relevant_variables = [
            *self.relevant_user_variables,
            *self.relevant_child_variables,
        ]

        self.hardcoded_id_map = {
            # Variable names to the relevant ID...
            "FK05_01": 5,
            "FK05_02": 6,
            "FK05_03": 7,
            "FK05_04": 8,
            "FK05_05": 9,
            "FK05_06": 10,  # With additional answer "Andere Diagnosen: [01]"
            "FK05_07": 11,
            "FK07": 13,
            "FK09": 17,  # ignore FK08_01
            "FK10": 18,  # ignore FK08_02
            "FK11": 19,
            "FK12": 20,
            "FK03": 3,  # Related to questions 21 & 22
            "FK04_01": 4,  # Related to questions 21 & 22
            # User Questions mapped to numeric IDs
            "FP01": 13,  # Eltern giant question
            "FP02": 13,  # Eltern giant question
            "FP03": 13,  # Eltern giant question
            "FP04": 13,  # The "andere" option
            "FE08": 7,
            "FE07": 6,
            "FE06": 5,
            "FE04": 4,  # Muttersprache
            "FE05_01": 4,  # Muttersprache (andere option)
            "FE02": 3,  # Nationalität
            "FE03_01": 3,  # Nationalität (andere option)
        }

        self.hardcoded_other_answers = {
            self.andere_diagnosen_other_question_variable: "FK05_06",
            self.nationality_other_question_variable: "FE02",
            self.muttersprache_other_question_variable: "FE04",
        }

    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def get_question_filled_in_to_parent(
        self, questions_df: pd.DataFrame, variable: str, debug_print: bool = False
    ) -> bool:
        """Check if a question is filled in by the parent."""
        csv_match = questions_df[questions_df["variable"] == variable]

        match_found = not csv_match.empty and str(csv_match.iloc[0]["isToParent"]) in [
            "true",
            "ja",
            "yes",
        ]

        if debug_print:
            logger.debug(
                f"Is to parent variable was: {'True' if match_found else 'False'}"
            )

        return match_found

    def get_question_filled_in_required(
        self, questions_df: pd.DataFrame, variable: str
    ) -> bool:
        """Check if a question is required."""
        # Original implementation always returns False
        return False

    def get_childs_parent_id(self, session: Session, case_id: int) -> int:
        """Get the parent ID for a child."""
        child_name = f"Imported Child {case_id}"
        child_result = session.execute(
            select(Child).where(Child.name == child_name)
        ).first()

        if child_result is not None:
            child = child_result[0]
            logger.debug(
                f"Found child: {child.id}, {child.name}, parent: {child.user_id}"
            )
            return child.user_id
        else:
            logger.error(f"Child with ID {case_id} not found")
            raise ValueError(f"Child with ID {case_id} not found")

    async def check_parent_exists(
        self, user_session: AsyncSession, case_id: int
    ) -> User | None:
        """Check if a parent exists for a child."""
        email = f"parent_of_{case_id}@artificialimporteddata.csv"
        logger.debug(f"Checking for parent with email: {email}")

        stmt = select(User).where(User.email == email)
        result = await user_session.execute(stmt)
        existing_parent = result.scalars().first()

        logger.debug(f"Existing parent: {existing_parent}")
        return existing_parent

    async def create_parent_for_child(
        self, user_session: AsyncSession, case_id: int
    ) -> User:
        """Create a parent user for a child."""
        username = f"parent_of_{case_id}"
        email = f"{username}@artificialimporteddata.csv"

        user_create = UserCreate(
            email=email,
            password="$$$$testUser$$$$432hjdfioj3409lk",
            is_researcher=False,
            full_data_access=False,
            research_group_id=0,
        )

        user = User(
            email=user_create.email,
            hashed_password="$$$$testUser$$$$432hjdfioj3409lk$$$$hashed$$$$",
            is_active=True,
            is_superuser=False,
            is_verified=False,
            is_researcher=user_create.is_researcher or False,
            full_data_access=user_create.full_data_access or False,
            research_group_id=user_create.research_group_id or 0,
        )

        user_session.add(user)
        await user_session.flush()

        logger.info(
            f"Created parent for child ID: {case_id} with email: {user_create.email}"
        )
        return user

    async def generate_parents_for_children(
        self, child_ids: list[int]
    ) -> dict[str, int]:
        """Generate parents for children."""
        child_parent_map = {}

        async with AsyncSession(
            self.data_manager.async_users_engine
        ) as user_import_session:
            user_db = SQLAlchemyUserDatabase(user_import_session, User)

            for child_id in child_ids:
                existing_parent = await self.check_parent_exists(
                    user_import_session, child_id
                )

                if existing_parent:
                    child_parent_map[str(child_id)] = existing_parent.id
                else:
                    parent = await self.create_parent_for_child(
                        user_import_session, child_id
                    )
                    logger.info(f"Created parent {parent.id} for child {child_id}")
                    child_parent_map[str(child_id)] = parent.id

            await user_import_session.commit()

        logger.debug(f"Final child_parent_map: {child_parent_map}")
        self.child_parent_map = child_parent_map
        return child_parent_map
        # not updating Child.user_id here. Could do that.

    def find_milestone_based_on_label(self, session: Session, label: str) -> int | None:
        """Find a milestone based on its label."""
        if ":" in label:
            label = label.split(":", 1)[1].lstrip()

        logger.debug(
            f"Milestone search - using preprocessed label for desc search as: {label}"
        )

        # Try exact match first
        stmt = select(MilestoneText).where(MilestoneText.desc == label)
        milestone_text = session.scalars(stmt).first()

        if not milestone_text:
            stmt = select(MilestoneText).where(MilestoneText.desc == label.rstrip("."))
            milestone_text = session.scalars(stmt).first()

        # Some German translations are missing the starting "Das"
        if not milestone_text:
            dasified_label = label.removeprefix("Das ")
            if dasified_label == "Kind erkennt, ob sich zwei Worte reimen oder nicht.":
                dasified_label = "Kind erkennt, ob sich zwei Worte reimen oder nicht. "
            if (
                dasified_label
                == "Kind erkennt, wenn Wörter mit dem gleichen Buchstaben beginnen (z.B. Haus/Hose, Brot/Besen, Ampel/Apfel)."
            ):
                dasified_label = "Kind erkennt, wenn Wörter mit dem gleichen Buchstaben beginnen (z.B. Haus/Hose, Brot/Besen, Ampel/Apfel."

            logger.debug(f"Trying with Dasified label: {dasified_label}")
            stmt = select(MilestoneText).where(MilestoneText.desc == dasified_label)
            milestone_text = session.scalars(stmt).first()

        # If all direct matches fail, try fuzzy matching
        if not milestone_text:
            logger.debug("Direct matches failed. Trying fuzzy matching...")
            stmt = select(MilestoneText)
            all_milestone_texts = session.scalars(stmt).all()

            best_match = None
            best_score = 0
            threshold = 85  # Minimum score to consider a match

            for mt in all_milestone_texts:
                if mt.desc:
                    score = fuzz.partial_ratio(label, mt.desc)
                    if score > best_score and score >= threshold:
                        best_score = score
                        best_match = mt

            if best_match:
                logger.debug(f"Found fuzzy match with score {best_score}:")
                logger.debug(f"Original: {label}")
                logger.debug(f"Matched:  {best_match.desc}")
                milestone_text = best_match

        if milestone_text:
            return milestone_text.milestone_id
        return None

    def update_milestone_with_name_property(
        self, session: Session, milestone_id: int, var: str
    ) -> bool:
        """Update a milestone with a name property."""
        stmt = select(Milestone).where(Milestone.id == milestone_id)
        milestone = session.scalars(stmt).first()

        if milestone:
            milestone.name = var
            session.commit()
            return True
        return False

    def derive_milestone_group_from_milestone_string_id(
        self, string_id: str
    ) -> str | None:
        """Derive the milestone group from a milestone string ID."""
        if len(string_id) > 2 and string_id[0:2] in self.milestone_group_id_map:
            return self.milestone_group_id_map[string_id[0:2]]
        return None

    def is_milestone(self, row: pd.Series) -> bool:
        """Check if a row represents a milestone."""
        var = row["VAR"]
        label = row["LABEL"]
        d_type = row.get("TYPE", "")
        input_type = row.get("INPUT", "")

        if not (isinstance(var, str) and "_" in var):
            return False
        if d_type != "ORDINAL":
            return False
        if input_type != "SCALE":
            return False
        if not label:
            return False
        return len(label) > 10

    def extract_milestone_prefix(self, text: str) -> str | None:
        """Extract the prefix from a milestone title."""
        if ":" in text:
            return text.split(":", 1)[0].strip()
        return None

    def clean_milestone_title(self, text: str) -> str:
        """Clean a milestone title."""
        if ":" in text:
            return text.split(":", 1)[1].strip()
        return text.strip()

    def create_answer(
        self,
        session: Session,
        user_or_child_id: int,
        question_id: int,
        answer_text: str,
        set_only_additional_answer: bool = False,
        is_child_question: bool = True,
    ) -> tuple[bool, ChildAnswer | UserAnswer]:
        """Create an answer for a question."""
        logger.debug(f"Creating answer for question {question_id}: {answer_text}")
        logger.debug(f"{'Child question' if is_child_question else 'User question'}")

        if set_only_additional_answer:
            logger.debug(
                "Additional answer with no found base question. This could be a question which is independent, "
                "but happens to have [01] and 'Andere' in the name, like 'Andere Diagnosen', which is okay, "
                "but it could indicate data processing has gone wrong."
            )

        try:
            logger.debug(f"Creating new answer: {answer_text}")

            if is_child_question:
                new_answer = ChildAnswer(
                    child_id=user_or_child_id,
                    question_id=question_id,
                    answer=answer_text,
                )
            else:
                new_answer = UserAnswer(
                    user_id=user_or_child_id,
                    question_id=question_id,
                    answer=answer_text,
                )

            session.add(new_answer)
            logger.debug(f"Added new answer: {new_answer}")
            return False, new_answer

        except Exception as e:
            logger.error(f"Error creating new answer: {e}")
            session.rollback()
            raise

    def should_be_saved(self, variable: str) -> bool:
        """Check if a variable should be saved."""
        return variable in self.all_relevant_variables

    def process_special_answer(
        self,
        session: Session,
        question_label: str,
        answer: str,
        variable: str,
        child_id: int,
    ) -> bool:
        """
        Process special answers that need custom handling.

        Returns:
            bool: True if the answer was processed, False otherwise
        """
        # Handle child age questions
        if variable in self.child_age_questions_labels:
            logger.debug("Age of birth case - skip, no need to save anything.")
            return True

        # Handle Eltern questions
        elif variable in self.eltern_question_variables:
            if variable == "FP03":  # Special Eltern overview
                logger.debug("(skipping general overall Eltern answer)")
                return True  # The specific minor ones which are not null will be saved instead

            logger.debug(
                f"Variable: {variable}, Question Label: {question_label}, "
                f"Was in eltern! So adding its answer: {answer}"
            )

            eltern_question_special_id = 13
            logger.debug(
                f"Using special Eltern question ID: {eltern_question_special_id}"
            )

            if answer is not None and len(answer) > 0:
                # Save parent answer for this question, only if it was actually filled out
                self.create_answer(
                    session,
                    user_or_child_id=self.get_childs_parent_id(session, child_id),
                    question_id=eltern_question_special_id,
                    answer_text=answer,
                    set_only_additional_answer=False,
                    is_child_question=False,
                )
                return True

        # Handle Fruhgeboren/Termingeboren questions
        elif variable in self.fruhbgeboren_and_teringeboren_variables:
            # Termingeboren/Fruhgeboren = 3
            # Fruhgeboren [01] = 4 (Weeks only if the former is "Fruhgeboren")
            pregnancy_duration_question_id = 21
            incubator_weeks_question_id = 22
            pregnanacy_duration_answer = 41  # 41 weeks assumed if Termingeboren
            incubator_weeks = 0

            # First bit is Fruhgeboren specific weeks part
            if variable == "FK04_01" and answer is not None and len(answer):
                # Parse weeks from the answer
                pregnanacy_duration_answer, incubator_weeks = parse_weeks(answer)

            # Create answers for pregnancy duration and incubator weeks
            self.create_answer(
                session,
                user_or_child_id=child_id,
                question_id=pregnancy_duration_question_id,
                answer_text=str(pregnanacy_duration_answer),
                set_only_additional_answer=False,
                is_child_question=False,
            )

            self.create_answer(
                session,
                user_or_child_id=child_id,
                question_id=incubator_weeks_question_id,
                answer_text=str(incubator_weeks),
                set_only_additional_answer=False,
                is_child_question=False,
            )

            return True

        # Handle younger/older sibling questions
        elif variable in self.younger_older_sibling_variables:
            relevant_question_id = 18 if question_label == "Jüngere Geschwister" else 17
            logger.debug(f"Setting special case younger siblings to: {answer}")

            self.create_answer(
                session,
                user_or_child_id=child_id,
                question_id=relevant_question_id,
                answer_text=answer
                if answer is not None and len(str(answer)) > 0
                else "0",
                set_only_additional_answer=False,
                is_child_question=True,
            )

            return True
        logger.debug(f"Not a special case variable: {question_label}")
        return False

    # -------------------------------------------------------------------------
    # Import Methods
    # -------------------------------------------------------------------------

    def import_milestones_metadata(self, session: Session) -> None:
        """Import milestones metadata."""
        logger.info("Importing milestones metadata")

        df = self.data_manager.load_milestones_metadata_df()

        # Filter for milestone rows
        milestone_df = df[df["VAR"].str.contains("_")]

        # Ensure German language exists
        if not session.get(Language, "de"):
            session.add(Language(id="de"))
            session.commit()

        # Group milestones by their prefixes
        milestone_groups = {}
        affix_groups = {}

        # First, identify affixes from the QUESTION column
        for _, row in milestone_df.iterrows():
            var = row["VAR"]
            label = row["LABEL"]
            question = row.get("QUESTION", "")

            if not self.is_milestone(row):
                logger.debug(f"Skipping {label}")
                continue
            else:
                logger.debug(f"Keeping {label}")

            # Check if this is an affix group
            if (
                isinstance(question, str)
                and question.startswith("__")
                and question.endswith("__")
            ):
                affix = question.removeprefix("__").removesuffix("__")
                if affix not in affix_groups:
                    affix_groups[affix] = []
                affix_groups[affix].append(var)

        # Now process all milestones and assign them to groups
        for _, row in milestone_df.iterrows():
            var = row["VAR"]
            label = row["LABEL"]

            if not self.is_milestone(row):
                continue

            derived_milestone_group = (
                self.derive_milestone_group_from_milestone_string_id(var)
            )

            # Get the prefix from the label
            prefix = self.extract_milestone_prefix(label)

            # Check if it belongs to an affix group
            for affix, vars_list in affix_groups.items():
                if var in vars_list:
                    prefix = affix if not prefix else affix + " " + prefix
                    break

            if derived_milestone_group:
                if derived_milestone_group not in milestone_groups:
                    milestone_groups[derived_milestone_group] = []
                milestone_groups[derived_milestone_group].append((var, label))
            elif prefix:
                if prefix not in milestone_groups:
                    milestone_groups[prefix] = []
                milestone_groups[prefix].append((var, label))

        # Update milestones with name property
        missing = 0
        for _order, (_prefix, milestones) in enumerate(
            milestone_groups.items(), start=1
        ):
            for _milestone_order, (var, label) in enumerate(milestones, start=1):
                milestone_id = self.find_milestone_based_on_label(session, label)

                if not milestone_id:
                    logger.warning("Unaccounted for milestone!")
                    missing += 1
                    if missing == 1:  # Only one exception, milestone 92
                        milestone_id = 92
                    else:
                        raise ValueError("At least 2 missing milestones.")

                self.update_milestone_with_name_property(session, milestone_id, var)
                logger.debug(f"Updated milestone {milestone_id} with name {var}")

        logger.info(f"Missing milestones: {missing}")
        session.commit()
        logger.info(
            f"Successfully imported {sum(len(m) for m in milestone_groups.values())} "
            f"milestones in {len(milestone_groups)} groups"
        )

    async def import_children_with_milestone_data(
        self, session: Session, data_df
    ) -> None:
        """Import children with milestone data."""
        logger.info("Importing children with milestone data")

        # Get all milestones
        milestone_query = select(Milestone)
        milestones = session.execute(milestone_query).scalars().all()

        # Create mappings
        self.milestone_mapping = {}
        self.milestone_group_mapping = {}

        for milestone in milestones:
            if milestone.name:
                self.milestone_mapping[milestone.name] = milestone.id
                self.milestone_group_mapping[milestone.id] = milestone.group_id

        # Generate parents for children
        child_ids = [row["CASE"] for _, row in data_df.iterrows()]
        print(f"There was ${len(child_ids)} children to import..")
        self.child_parent_map = await self.generate_parents_for_children(child_ids)

        # Process each row (child)
        for _, row in data_df.iterrows():
            child_id = row["CASE"]

            if str(row["FK01"]) == "-9" or str(row["FK02"]) == "-9":
                logger.warning(
                    f"Skipping child {child_id} who is missing essential birth month/year data"
                )
                continue

            # Get parent ID
            parent_id = self.child_parent_map[str(child_id)]

            # Create child
            child = Child(
                name=f"Imported Child {child_id}",
                birth_year=self.birth_year_mapping[int(row["FK01"])],
                birth_month=self.birth_month_mapping[int(row["FK02"])],
                user_id=parent_id,
                has_image=False,
            )
            session.add(child)
            session.commit()
            logger.info(f"Created child with ID: {child.id}")

            # Create milestone answer session
            answer_session = MilestoneAnswerSession(
                child_id=child.id,
                user_id=parent_id,
                expired=True,
                included_in_statistics=False,
                created_at=datetime(2025, 1, 1, 1, 0, 1),
                suspicious=False,
            )
            session.add(answer_session)
            session.commit()

            # Process each milestone column
            for column, milestone_id in self.milestone_mapping.items():
                if column in row:
                    answer_value = row[column]

                    # Skip if not answered
                    if (
                        answer_value == "-9"
                        or answer_value == ""
                        or pd.isna(answer_value)
                        or str(answer_value).lower() == "nan"
                    ):
                        continue

                    # Convert and adjust answer
                    try:
                        answer_int = int(float(str(answer_value).strip()))
                        if 1 <= answer_int <= 4:
                            adjusted_answer = answer_int - 1

                            # Create milestone answer
                            milestone_answer = MilestoneAnswer(
                                answer_session_id=answer_session.id,
                                milestone_id=milestone_id,
                                milestone_group_id=self.milestone_group_mapping.get(
                                    milestone_id
                                ),
                                answer=adjusted_answer,
                            )
                            session.add(milestone_answer)
                    except (ValueError, TypeError) as err:
                        raise ValueError(
                            f"Unable to save milestone {column} with value {answer_value}"
                        ) from err

            # Commit all answers for this child
            session.commit()

    def import_questions(self, session: Session) -> None:
        """Import questions."""
        logger.info("Importing questions")

        labels_df = self.data_manager.load_labels_df()
        questions_configured_df = self.data_manager.load_questions_configured_df()

        # Filter out milestones
        labels_df = labels_df.loc[(labels_df.index > 170) & (labels_df.index < 395)]

        free_text_questions = []
        previous_variable_label = None
        processed_variables = set()

        for _, label_row in (
            labels_df.groupby("Variable").first().reset_index().iterrows()
        ):
            variable = label_row["Variable"]

            # Skip if already processed
            if variable in processed_variables:
                continue
            processed_variables.add(variable)

            # Determine question type and properties
            variable_type = label_row["Variable Type"]
            input_type = label_row["Input Type"]
            variable_label = label_row["Variable Label"]

            # Handle different variable types
            if (
                (variable_type == "NOMINAL" or variable_type == "ORDINAL")
                and input_type == "MC"
            ) or (variable_type == "DICHOTOMOUS" and input_type == "CK"):
                # Multiple Choice Question
                options = labels_df[labels_df["Variable"] == variable]

                # Filter out non-response codes
                valid_options = options[options["Response Code"] != -9]

                # Prepare options
                options_dict = {
                    str(row["Response Code"]): row["Response Label"]
                    for _, row in valid_options.iterrows()
                }

                # Prepare options JSON
                prepared_options = []
                options_display = []

                for _, row in valid_options.iterrows():
                    escaped_label = row["Response Label"].replace(",", "&#44;")

                    option = {
                        "value": str(row["Response Code"]),
                        "name": escaped_label,
                        "disabled": False,
                    }
                    prepared_options.append(option)
                    options_display.append(escaped_label)

                import json

                options_json = json.dumps(prepared_options)
                options_str = ";".join(options_display)

                # Save select question
                is_to_parent = self.get_question_filled_in_to_parent(
                    questions_configured_df, variable
                )
                is_required = self.get_question_filled_in_required(
                    questions_configured_df, variable
                )

                if is_to_parent:
                    # Check for existing UserQuestion
                    existing_question = session.execute(
                        select(UserQuestion).where(UserQuestion.name == variable_label)
                    ).scalar_one_or_none()

                    if not existing_question:
                        # Create UserQuestion
                        user_question = UserQuestion(
                            component="select",
                            type="text",
                            required=is_required,
                            name=variable_label,
                            text={
                                "de": UserQuestionText(
                                    question=variable_label,
                                    options_json=options_json,
                                    options=options_str,
                                    lang_id="de",
                                )
                            },
                        )
                        session.add(user_question)
                else:
                    # Check for existing ChildQuestion
                    existing_question = session.execute(
                        select(ChildQuestion).where(
                            ChildQuestion.name == variable_label
                        )
                    ).scalar_one_or_none()

                    if not existing_question:
                        # Create ChildQuestion
                        child_question = ChildQuestion(
                            component="select",
                            type="text",
                            required=is_required,
                            name=variable_label,
                            text={
                                "de": ChildQuestionText(
                                    question=variable_label,
                                    options_json=options_json,
                                    options=options_str,
                                    lang_id="de",
                                )
                            },
                        )
                        session.add(child_question)

                # Track previous variable for 'Andere' handling
                previous_variable_label = variable_label

            elif variable_type == "TEXT" and input_type == "TXT":
                # Check if this is an 'Andere' option for a previous question
                if (
                    type(variable_label) is str
                    and ": [01]" in variable_label
                    and (
                        previous_variable_label
                        and f"{previous_variable_label}: [01]" in variable_label
                    )
                ):
                    logger.debug(
                        "Not creating question for this Other option - its free text response will be merged"
                    )
                    continue

                # Independent free text question
                free_text_questions.append((variable, variable_label))

                # Save text question
                is_to_parent = self.get_question_filled_in_to_parent(
                    questions_configured_df, variable
                )
                is_required = self.get_question_filled_in_required(
                    questions_configured_df, variable
                )

                if is_to_parent:
                    # Check for existing UserQuestion
                    existing_question = session.execute(
                        select(UserQuestion).where(UserQuestion.name == variable_label)
                    ).scalar_one_or_none()

                    if not existing_question:
                        # Create UserQuestion
                        user_question = UserQuestion(
                            component="textarea",
                            type="text",
                            required=is_required,
                            name=variable_label,
                            text={
                                "de": UserQuestionText(
                                    question=variable_label,
                                    lang_id="de",
                                )
                            },
                        )
                        session.add(user_question)
                else:
                    # Check for existing ChildQuestion
                    existing_question = session.execute(
                        select(ChildQuestion).where(
                            ChildQuestion.name == variable_label
                        )
                    ).scalar_one_or_none()

                    if not existing_question:
                        # Create ChildQuestion
                        child_question = ChildQuestion(
                            component="textarea",
                            type="text",
                            required=is_required,
                            name=variable_label,
                            text={
                                "de": ChildQuestionText(
                                    question=variable_label,
                                    lang_id="de",
                                )
                            },
                        )
                        session.add(child_question)

        session.commit()
        logger.info("Questions imported successfully")

    def import_answers(self, session: Session, data_df) -> None:
        """Import answers to questions."""
        logger.info("Importing answers to questions")

        labels_df = self.data_manager.load_labels_df()
        questions_configured_df = self.data_manager.load_questions_configured_df()

        # Filter out milestones
        labels_df = labels_df.loc[(labels_df.index > 170) & (labels_df.index < 395)]

        questions_to_discard = ["FK01", "FK02"]  # Already assigned to each child
        total_answers = 0
        missing = 0

        # Get child mapping
        child_case_to_id_map = {}
        children = session.exec(
            select(Child.id, Child.name).where(Child.name.like("Imported Child %"))
        ).all()

        for child_id, child_name in children:
            if child_name.startswith("Imported Child "):
                try:
                    case_id = child_name.replace("Imported Child ", "")
                    child_case_to_id_map[case_id] = child_id
                except Exception as e:
                    logger.error(f"Error processing child name '{child_name}': {e}")

        # Process data into answers
        for _, child_row in data_df.iterrows():
            logger.debug(f"Processing child {child_row.get('CASE')}")

            for _, label_row in (
                labels_df.groupby("Variable").first().reset_index().iterrows()
            ):
                db_child_id = child_case_to_id_map[str(child_row.get("CASE"))]
                variable_type = label_row["Variable Type"]
                variable = label_row["Variable"]
                variable_label = label_row["Variable Label"]

                if variable_label in questions_to_discard:
                    continue

                # Skip variables not in hardcoded_id_map for additional data
                if variable not in self.hardcoded_id_map:
                    continue

                response = child_row.get(variable)

                # Skip if no response or -9 (not answered)
                if pd.isna(response) or response == -9:
                    continue

                # Check if this is a special case that needs custom processing
                if self.should_be_saved(variable):
                    response_label = labels_df[
                        (labels_df["Variable"] == variable)
                        & (labels_df["Response Code"] == response)
                    ]

                    if response_label.empty:
                        continue  # No data entered

                    answer = (
                        response_label.iloc[0]["Response Label"]
                        if (
                            variable_type == "NOMINAL"
                            or variable_type == "ORDINAL"
                            or variable_type == "DICHOTOMOUS"
                        )
                        else response_label
                    )

                    # Process special answers (Eltern, Fruhgeboren, etc.)
                    have_acted_upon_question = self.process_special_answer(
                        session, variable_label, answer, variable, child_row.get("CASE")
                    )

                    if have_acted_upon_question:
                        continue

                preserved_freetext_lookup_key = variable
                set_only_additional_answer = False

                # Check if this is an 'Andere' option
                if variable in self.hardcoded_other_answers:
                    set_only_additional_answer = True
                    variable = self.hardcoded_other_answers[variable]

                # Find the corresponding question
                child_query = select(ChildQuestion).where(
                    ChildQuestion.id == self.hardcoded_id_map[variable]
                )
                user_query = select(UserQuestion).where(
                    UserQuestion.id == self.hardcoded_id_map[variable]
                )

                question = session.exec(
                    child_query
                    if variable in self.relevant_child_variables
                    else user_query
                ).first()

                if not question:
                    logger.warning(
                        f"Discarding question answer without found saved question: "
                        f"{variable}, {label_row['Variable Label']}"
                    )
                    questions_to_discard.append(variable)
                    continue

                # Handle Multiple Choice
                if (
                    variable_type == "NOMINAL"
                    or variable_type == "ORDINAL"
                    or variable_type == "DICHOTOMOUS"
                ):
                    response_label = labels_df[
                        (labels_df["Variable"] == variable)
                        & (labels_df["Response Code"] == response)
                    ]

                    if not response_label.empty:
                        answer_text = response_label.iloc[0]["Response Label"]

                        # Check if question is for parent or child
                        if self.get_question_filled_in_to_parent(
                            questions_configured_df, variable
                        ):
                            # Create user answer
                            parent_id = self.get_childs_parent_id(
                                session, child_row.get("CASE")
                            )
                            _, answer = self.create_answer(
                                session,
                                user_or_child_id=parent_id,
                                question_id=question.id,
                                answer_text=answer_text,
                                set_only_additional_answer=set_only_additional_answer,
                                is_child_question=False,
                            )
                        else:
                            # Create child answer
                            _, answer = self.create_answer(
                                session,
                                user_or_child_id=db_child_id,
                                question_id=question.id,
                                answer_text=answer_text,
                                set_only_additional_answer=set_only_additional_answer,
                                is_child_question=True,
                            )

                        total_answers += 1
                        session.add(answer)

                # Handle Text
                elif variable_type == "TEXT":
                    # Check if this is an 'Andere' option for a previous question
                    if " [01]" in variable_label and "Andere" in variable_label:
                        logger.debug(
                            f"Free text Andere triggered! {variable}, {variable_label}"
                        )
                        set_only_additional_answer = True

                    response = child_row.get(preserved_freetext_lookup_key)
                    answer_text = str(response)

                    # Skip if 'nan' or None for additional answers
                    if set_only_additional_answer and (
                        answer_text == "nan" or answer_text is None
                    ):
                        logger.debug("Skipping save due to 'nan' additional answer")
                        continue

                    # Check if question is for parent or child
                    if self.get_question_filled_in_to_parent(
                        questions_configured_df, variable
                    ):
                        # Create user answer
                        parent_id = self.get_childs_parent_id(
                            session, child_row.get("CASE")
                        )
                        _, answer = self.create_answer(
                            session,
                            user_or_child_id=parent_id,
                            question_id=question.id,
                            answer_text=answer_text,
                            set_only_additional_answer=set_only_additional_answer,
                            is_child_question=False,
                        )
                    else:
                        # Create child answer
                        _, answer = self.create_answer(
                            session,
                            user_or_child_id=db_child_id,
                            question_id=question.id,
                            answer_text=answer_text,
                            set_only_additional_answer=set_only_additional_answer,
                            is_child_question=True,
                        )

                    total_answers += 1
                    session.add(answer)

                else:
                    logger.warning(
                        f"Variable type has no clear processing method: {variable_type}, {variable_label}"
                    )
                    missing += 1

        session.commit()
        logger.info(f"Total answers saved: {total_answers}")
        logger.info(f"Missing answers: {missing}")

    async def import_additional_data(self, session: Session) -> None:
        """Import additional data."""
        logger.info("Importing additional data")

        if not self.data_manager.import_paths.additional_data_path:
            logger.warning("No additional data path provided")
            return

        additional_data_df = self.data_manager.load_additional_data_df()

        # First import children with milestone data
        await self.import_children_with_milestone_data(session, additional_data_df)

        # Then import answers
        self.import_answers(session, additional_data_df)

        # Run post-processing corrections
        run_postprocessing_corrections(
            str(self.data_manager.import_paths.additional_data_path), dry_run=False
        )

        logger.info("Additional data imported successfully")

    # -------------------------------------------------------------------------
    # Main Import Methods
    # -------------------------------------------------------------------------

    async def run_full_import(self) -> None:
        """Run a full import of all data."""
        logger.info("Starting full import")

        # Get sessions
        import_session, _ = self.data_manager.get_import_session(create_tables=True)
        data_df = data_df = self.data_manager.load_data_df()

        try:
            # Import milestones metadata
            self.import_milestones_metadata(import_session)

            # Import children with milestone data
            await self.import_children_with_milestone_data(import_session, data_df)

            # Import questions
            self.import_questions(import_session)

            # Import answers
            self.import_answers(import_session, data_df)

            logger.info("Full import completed successfully")

        except Exception as e:
            logger.error(f"Error during import: {e}")
            import_session.rollback()
            raise

    async def run_additional_data_import(self) -> None:
        """Run import of additional data."""
        logger.info("Starting additional data import")

        # Get sessions
        import_session, _ = self.data_manager.get_current_session()

        try:
            # Import additional data
            await self.import_additional_data(import_session)

            logger.info("Additional data import completed successfully")

        except Exception as e:
            logger.error(f"Error during additional data import: {e}")
            import_session.rollback()
            raise
