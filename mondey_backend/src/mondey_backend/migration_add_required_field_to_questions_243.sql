-- Needs to be ran on the production DB so it will continue to work with the changed class Question abstract class
ALTER TABLE userquestion ADD COLUMN required BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE childquestion ADD COLUMN required BOOLEAN NOT NULL DEFAULT FALSE;
