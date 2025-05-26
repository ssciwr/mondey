DROP TABLE childmilestoneexpectedagerange;
DROP TABLE milestoneagescorecollection;
DROP TABLE milestoneagescore;
ALTER TABLE milestone ADD COLUMN expected_age_delta INTEGER DEFAULT 6;
