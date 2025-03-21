ALTER TABLE milestone ADD COLUMN data_import_key VARCHAR DEFAULT NULL;
CREATE INDEX idx_milestones_data_import_key ON milestone(data_import_key);
