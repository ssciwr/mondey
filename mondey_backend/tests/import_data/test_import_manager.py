"""
Tests for the ImportManager class.

These tests verify that the ImportManager correctly handles data import operations.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from mondey_backend.import_data.manager import ImportManager
from mondey_backend.import_data.manager.import_manager import ImportPaths
from mondey_backend.models.children import Child
from mondey_backend.models.milestones import Language, Milestone, MilestoneText
from mondey_backend.models.questions import ChildQuestion, UserQuestion


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        yield Path(f.name)


@pytest.fixture
def import_paths():
    """Create test import paths."""
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Create test CSV files
        labels_path = temp_dir_path / "labels.csv"
        data_path = temp_dir_path / "data.csv"
        questions_path = temp_dir_path / "questions.csv"
        milestones_path = temp_dir_path / "milestones.csv"
        additional_data_path = temp_dir_path / "additional_data.csv"
        
        # Create minimal test data
        pd.DataFrame({
            "Variable": ["TEST01", "TEST01", "TEST02"],
            "Variable Type": ["NOMINAL", "NOMINAL", "TEXT"],
            "Input Type": ["MC", "MC", "TXT"],
            "Variable Label": ["Test Question 1", "Test Question 1", "Test Question 2"],
            "Response Code": [1, 2, None],
            "Response Label": ["Option 1", "Option 2", None]
        }).to_csv(labels_path, sep=",", encoding="utf-16", index=False)
        
        pd.DataFrame({
            "CASE": [1, 2],
            "FK01": [1, 2],  # Birth year
            "FK02": [1, 2],  # Birth month
            "TEST01": [1, 2],
            "TEST02": ["Text answer 1", "Text answer 2"]
        }).to_csv(data_path, sep="\t", encoding="utf-16", index=False)
        
        pd.DataFrame({
            "variable": ["TEST01", "TEST02"],
            "question": ["Test Question 1", "Test Question 2"],
            "isRequired": ["false", "false"],
            "isToParent": ["false", "true"]
        }).to_csv(questions_path, sep=",", encoding="utf-8", index=False)
        
        pd.DataFrame({
            "VAR": ["GM_01", "HM_01"],
            "LABEL": ["Grobmotorik: Test Milestone 1", "Handmotorik: Test Milestone 2"],
            "TYPE": ["ORDINAL", "ORDINAL"],
            "INPUT": ["SCALE", "SCALE"],
            "QUESTION": ["__Grobmotorik__", "__Handmotorik__"]
        }).to_csv(milestones_path, sep="\t", encoding="utf-16", index=False)
        
        pd.DataFrame({
            "CASE": [3],
            "FK01": [3],  # Birth year
            "FK02": [3],  # Birth month
            "TEST01": [1],
            "TEST02": ["Additional text answer"]
        }).to_csv(additional_data_path, sep="\t", encoding="utf-16", index=False)
        
        yield ImportPaths(
            labels_path=labels_path,
            data_path=data_path,
            questions_configured_path=questions_path,
            milestones_metadata_path=milestones_path,
            additional_data_path=additional_data_path
        )


@pytest.fixture
def import_manager(temp_db_path, import_paths):
    """Create an ImportManager with test paths."""
    # Create test database paths
    mondey_db_path = temp_db_path.with_name("mondey_test.db")
    current_db_path = temp_db_path.with_name("current_test.db")
    users_db_path = temp_db_path.with_name("users_test.db")
    
    # Create manager
    manager = ImportManager(
        import_paths=import_paths,
        mondey_db_path=mondey_db_path,
        current_db_path=current_db_path,
        users_db_path=users_db_path,
        debug=True
    )
    
    # Create test engines and tables
    engine = create_engine(f"sqlite:////{mondey_db_path}")
    SQLModel.metadata.create_all(engine)
    
    current_engine = create_engine(f"sqlite:////{current_db_path}")
    SQLModel.metadata.create_all(current_engine)
    
    # Add German language to current database
    with Session(current_engine) as session:
        session.add(Language(id="de"))
        
        # Add test milestones
        milestone1 = Milestone(id=1, group_id="2", order=1, expected_age_months=12)
        milestone2 = Milestone(id=2, group_id="1", order=2, expected_age_months=24)
        session.add(milestone1)
        session.add(milestone2)
        
        # Add test milestone texts
        session.add(MilestoneText(
            milestone_id=1,
            lang_id="de",
            title="Test Milestone 1",
            desc="Test Milestone 1"
        ))
        session.add(MilestoneText(
            milestone_id=2,
            lang_id="de",
            title="Test Milestone 2",
            desc="Test Milestone 2"
        ))
        
        session.commit()
    
    # Mock hardcoded mappings
    manager.hardcoded_id_map = {
        "TEST01": 1,
        "TEST02": 2
    }
    manager.hardcoded_other_answers = {}
    manager.relevant_child_variables = ["TEST01"]
    
    yield manager
    
    # Clean up
    if os.path.exists(mondey_db_path):
        os.remove(mondey_db_path)
    if os.path.exists(current_db_path):
        os.remove(current_db_path)
    if os.path.exists(users_db_path):
        os.remove(users_db_path)


class TestImportManager:
    """Tests for the ImportManager class."""
    
    def test_load_data(self, import_manager):
        """Test loading data from CSV files."""
        # Load data
        labels_df = import_manager.load_labels_df()
        data_df = import_manager.load_data_df()
        questions_df = import_manager.load_questions_configured_df()
        milestones_df = import_manager.load_milestones_metadata_df()
        additional_data_df = import_manager.load_additional_data_df()
        
        # Check data was loaded correctly
        assert len(labels_df) > 0
        assert len(data_df) > 0
        assert len(questions_df) > 0
        assert len(milestones_df) > 0
        assert len(additional_data_df) > 0
        
        # Check specific values
        assert "TEST01" in labels_df["Variable"].values
        assert 1 in data_df["CASE"].values
        assert "TEST01" in questions_df["variable"].values
        assert "GM_01" in milestones_df["VAR"].values
        assert 3 in additional_data_df["CASE"].values
    
    def test_get_question_filled_in_to_parent(self, import_manager):
        """Test checking if a question is filled in by the parent."""
        questions_df = import_manager.load_questions_configured_df()
        
        # TEST01 is not filled in by parent
        assert not import_manager.get_question_filled_in_to_parent(questions_df, "TEST01")
        
        # TEST02 is filled in by parent
        assert import_manager.get_question_filled_in_to_parent(questions_df, "TEST02")
    
    def test_derive_milestone_group(self, import_manager):
        """Test deriving milestone group from milestone string ID."""
        # Test valid milestone groups
        assert import_manager.derive_milestone_group_from_milestone_string_id("GM_01") == "2"
        assert import_manager.derive_milestone_group_from_milestone_string_id("HM_02") == "1"
        assert import_manager.derive_milestone_group_from_milestone_string_id("SE_03") == "5"
        
        # Test invalid milestone group
        assert import_manager.derive_milestone_group_from_milestone_string_id("XX_01") is None
        assert import_manager.derive_milestone_group_from_milestone_string_id("G") is None
    
    def test_is_milestone(self, import_manager):
        """Test checking if a row represents a milestone."""
        # Valid milestone
        valid_row = pd.Series({
            "VAR": "GM_01",
            "LABEL": "Test Milestone",
            "TYPE": "ORDINAL",
            "INPUT": "SCALE"
        })
        assert import_manager.is_milestone(valid_row)
        
        # Invalid milestone - wrong type
        invalid_row1 = pd.Series({
            "VAR": "GM_01",
            "LABEL": "Test Milestone",
            "TYPE": "NOMINAL",
            "INPUT": "SCALE"
        })
        assert not import_manager.is_milestone(invalid_row1)
        
        # Invalid milestone - wrong input
        invalid_row2 = pd.Series({
            "VAR": "GM_01",
            "LABEL": "Test Milestone",
            "TYPE": "ORDINAL",
            "INPUT": "MC"
        })
        assert not import_manager.is_milestone(invalid_row2)
        
        # Invalid milestone - no underscore in VAR
        invalid_row3 = pd.Series({
            "VAR": "GM01",
            "LABEL": "Test Milestone",
            "TYPE": "ORDINAL",
            "INPUT": "SCALE"
        })
        assert not import_manager.is_milestone(invalid_row3)
    
    @pytest.mark.asyncio
    async def test_generate_parents_for_children(self, import_manager):
        """Test generating parents for children."""
        # Mock check_parent_exists and create_parent_for_child
        import_manager.check_parent_exists = MagicMock(return_value=None)
        import_manager.create_parent_for_child = MagicMock(return_value=MagicMock(id=1))
        
        # Generate parents
        child_ids = [1, 2, 3]
        child_parent_map = await import_manager.generate_parents_for_children(child_ids)
        
        # Check results
        assert len(child_parent_map) == 3
        assert all(child_id in child_parent_map for child_id in ["1", "2", "3"])
        assert all(parent_id == 1 for parent_id in child_parent_map.values())
        
        # Check methods were called correctly
        assert import_manager.check_parent_exists.call_count == 3
        assert import_manager.create_parent_for_child.call_count == 3
    
    @pytest.mark.asyncio
    @patch("mondey_backend.import_data.manager.import_manager.select")
    async def test_import_milestones_metadata(self, mock_select, import_manager):
        """Test importing milestones metadata."""
        # Mock session and find_milestone_based_on_label
        session = MagicMock()
        import_manager.find_milestone_based_on_label = MagicMock(return_value=1)
        import_manager.update_milestone_with_name_property = MagicMock(return_value=True)
        
        # Import milestones metadata
        import_manager.import_milestones_metadata(session)
        
        # Check methods were called
        assert import_manager.find_milestone_based_on_label.call_count > 0
        assert import_manager.update_milestone_with_name_property.call_count > 0
        assert session.commit.called
    
    @pytest.mark.asyncio
    async def test_full_import(self, import_manager):
        """Test running a full import."""
        # Mock import methods
        import_manager.import_milestones_metadata = MagicMock()
        import_manager.import_children_with_milestone_data = MagicMock()
        import_manager.import_questions = MagicMock()
        import_manager.import_answers = MagicMock()
        
        # Run full import
        await import_manager.run_full_import()
        
        # Check methods were called
        assert import_manager.import_milestones_metadata.called
        assert import_manager.import_children_with_milestone_data.called
        assert import_manager.import_questions.called
        assert import_manager.import_answers.called
    
    @pytest.mark.asyncio
    async def test_additional_data_import(self, import_manager):
        """Test importing additional data."""
        # Mock import methods
        import_manager.import_additional_data = MagicMock()
        
        # Run additional data import
        await import_manager.run_additional_data_import()
        
        # Check methods were called
        assert import_manager.import_additional_data.called


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
