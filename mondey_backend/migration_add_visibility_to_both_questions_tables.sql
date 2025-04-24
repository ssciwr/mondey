ALTER TABLE childquestion
    ADD COLUMN visibility BOOLEAN DEFAULT false;

ALTER TABLE userquestion
    ADD COLUMN visibility BOOLEAN DEFAULT false;
