UPDATE milestoneanswersession SET suspicious_state = CASE WHEN suspicious = TRUE THEN 'suspicious' ELSE 'not_suspicious' END
