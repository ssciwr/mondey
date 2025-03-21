import os
import re
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session

# Import models
from mondey_backend.models.milestones import (
    Language,
    MilestoneGroup,
    MilestoneGroupText,
    Milestone,
    MilestoneText,
)

def extract_milestone_prefix(text):
    """Extract the prefix from a milestone title."""
    if ":" in text:
        return text.split(":", 1)[0].strip()
    return None

def clean_milestone_title(text):
    """Remove prefix and clean the milestone title."""
    if ":" in text:
        return text.split(":", 1)[1].strip()
    return text.strip()

def process_milestones_csv(csv_path):
    """Process the milestones CSV file and insert data into the database."""
    # Read the CSV file
    df = pd.read_csv(csv_path, sep="\t", encoding="utf-8")
    
    # Filter for milestone rows (those with IDs containing '_')
    milestone_df = df[df['VAR'].str.contains('_')]
    
    # Create a database connection
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./mondey.db")
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Ensure the German language exists
        if not session.get(Language, "de"):
            session.add(Language(id="de"))
            session.commit()
        
        # Group milestones by their prefixes
        milestone_groups = {}
        affix_groups = {}
        
        # First, identify affixes from the QUESTION column
        for _, row in milestone_df.iterrows():
            var = row['VAR']
            label = row['LABEL']
            question = row.get('QUESTION', '')
            
            # Skip non-milestone rows
            if not (isinstance(var, str) and '_' in var):
                continue
                
            # Check if this is an affix group
            if isinstance(question, str) and question.startswith('__') and question.endswith('__'):
                affix = question.strip('__')
                if affix not in affix_groups:
                    affix_groups[affix] = []
                affix_groups[affix].append(var)
        
        # Now process all milestones and assign them to groups
        for _, row in milestone_df.iterrows():
            var = row['VAR']
            label = row['LABEL']
            
            # Skip non-milestone rows
            if not (isinstance(var, str) and '_' in var):
                continue
            
            # Get the prefix from the label
            prefix = extract_milestone_prefix(label)
            
            # If no prefix, check if it belongs to an affix group
            if not prefix:
                for affix, vars_list in affix_groups.items():
                    if var in vars_list:
                        prefix = affix
                        break
            
            if prefix:
                if prefix not in milestone_groups:
                    milestone_groups[prefix] = []
                milestone_groups[prefix].append((var, label))
        
        # Create milestone groups and milestones
        group_id_map = {}  # To store group_id for each prefix
        
        for order, (prefix, milestones) in enumerate(milestone_groups.items(), start=1):
            # Create milestone group
            milestone_group = MilestoneGroup(order=order)
            session.add(milestone_group)
            session.flush()  # To get the ID
            
            # Create milestone group text
            milestone_group_text = MilestoneGroupText(
                group_id=milestone_group.id,
                lang_id="de",
                title=prefix,
                desc=""
            )
            session.add(milestone_group_text)
            
            group_id_map[prefix] = milestone_group.id
            
            # Create milestones for this group
            for milestone_order, (var, label) in enumerate(milestones, start=1):
                clean_title = clean_milestone_title(label)
                
                milestone = Milestone(
                    group_id=milestone_group.id,
                    order=milestone_order,
                    expected_age_months=12  # Default value, adjust as needed
                )
                session.add(milestone)
                session.flush()  # To get the ID
                
                # Create milestone text
                milestone_text = MilestoneText(
                    milestone_id=milestone.id,
                    lang_id="de",
                    title=clean_title,
                    desc="",
                    obs="",
                    help=""
                )
                session.add(milestone_text)
            
        session.commit()
        print(f"Successfully imported {sum(len(m) for m in milestone_groups.values())} milestones in {len(milestone_groups)} groups")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python insert_milestones_into_database.py <path_to_csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    process_milestones_csv(csv_path)
