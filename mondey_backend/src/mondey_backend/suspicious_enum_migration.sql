ALTER TABLE milestoneanswersession
    ADD COLUMN suspicious_state TEXT
        DEFAULT 'not_suspicious' NOT NULL
        CHECK (suspicious_state IN ('admin_not_suspicious', 'not_suspicious', 'suspicious', 'admin_suspicious'));

UPDATE milestoneanswersession
SET suspicious_state = CASE
                           WHEN suspicious = TRUE THEN 'suspicious'
                           ELSE 'not_suspicious'
END;
ALTER TABLE milestoneanswersession
DROP COLUMN suspicious;
