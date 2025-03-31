ALTER TABLE milestone ADD COLUMN name VARCHAR DEFAULT NULL;
CREATE INDEX idx_milestones_name ON milestone(name);
