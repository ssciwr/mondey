ALTER TABLE milestone
ADD COLUMN relevant_age_min INTEGER NOT NULL DEFAULT 6;

ALTER TABLE milestone
ADD COLUMN relevant_age_max INTEGER NOT NULL DEFAULT 18;

UPDATE milestone
SET relevant_age_min = CASE
    WHEN (expected_age_months - expected_age_delta) < 0 THEN 0
    WHEN (expected_age_months - expected_age_delta) > 72 THEN 72
    ELSE (expected_age_months - expected_age_delta)
END;

UPDATE milestone
SET relevant_age_max = CASE
    WHEN (expected_age_months + expected_age_delta) < 0 THEN 0
    WHEN (expected_age_months + expected_age_delta) > 72 THEN 72
    ELSE (expected_age_months + expected_age_delta)
END;

ALTER TABLE milestone
DROP COLUMN expected_age_delta;

DROP TABLE milestoneagescorecollection CASCADE;
