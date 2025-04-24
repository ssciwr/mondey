-- This script creates 7 additional children with milestone answer sessions
-- It should be run after importBaseMetadata.sql

-- Create 7 children with different ages
-- Child 1: 3 months old
INSERT INTO child (id, user_id, name, birth_year, birth_month, has_image, color)
VALUES (1001, 3, 'Emma Johnson',
        CASE
            WHEN strftime('%m', 'now') <= '03' THEN strftime('%Y', 'now') - 1
            ELSE strftime('%Y', 'now')
        END,
        CASE
            WHEN strftime('%m', 'now') <= '03' THEN strftime('%m', 'now') + 9
            ELSE strftime('%m', 'now') - 3
        END,
        false, '#ffcdd2');

-- Child 2: 8 months old
INSERT INTO child (id, user_id, name, birth_year, birth_month, has_image, color)
VALUES (1002, 3, 'Liam Smith',
        CASE
            WHEN strftime('%m', 'now') <= '08' THEN strftime('%Y', 'now') - 1
            ELSE strftime('%Y', 'now')
        END,
        CASE
            WHEN strftime('%m', 'now') <= '08' THEN strftime('%m', 'now') + 4
            ELSE strftime('%m', 'now') - 8
        END,
        false, '#bbdefb');

-- Child 3: 12 months old (1 year)
INSERT INTO child (id, user_id, name, birth_year, birth_month, has_image, color)
VALUES (1003, 3, 'Olivia Brown',
        CASE
            WHEN strftime('%m', 'now') = '01' THEN strftime('%Y', 'now') - 2
            ELSE strftime('%Y', 'now') - 1
        END,
        strftime('%m', 'now'),
        false, '#c8e6c9');

-- Child 4: 18 months old (1.5 years)
INSERT INTO child (id, user_id, name, birth_year, birth_month, has_image, color)
VALUES (1004, 4, 'Noah Davis',
        CASE
            WHEN strftime('%m', 'now') <= '06' THEN strftime('%Y', 'now') - 2
            ELSE strftime('%Y', 'now') - 1
        END,
        CASE
            WHEN strftime('%m', 'now') <= '06' THEN strftime('%m', 'now') + 6
            ELSE strftime('%m', 'now') - 6
        END,
        false, '#fff9c4');

-- Child 5: 24 months old (2 years)
INSERT INTO child (id, user_id, name, birth_year, birth_month, has_image, color)
VALUES (1005, 4, 'Ava Wilson',
        strftime('%Y', 'now') - 2,
        strftime('%m', 'now'),
        false, '#e1bee7');

-- Child 6: 30 months old (2.5 years)
INSERT INTO child (id, user_id, name, birth_year, birth_month, has_image, color)
VALUES (1006, 5, 'Ethan Miller',
        CASE
            WHEN strftime('%m', 'now') <= '06' THEN strftime('%Y', 'now') - 3
            ELSE strftime('%Y', 'now') - 2
        END,
        CASE
            WHEN strftime('%m', 'now') <= '06' THEN strftime('%m', 'now') + 6
            ELSE strftime('%m', 'now') - 6
        END,
        false, '#b2dfdb');

-- Child 7: 36 months old (3 years)
INSERT INTO child (id, user_id, name, birth_year, birth_month, has_image, color)
VALUES (1007, 5, 'Sophia Taylor',
        strftime('%Y', 'now') - 3,
        strftime('%m', 'now'),
        false, '#ffccbc');

-- Create milestone answer sessions for each child
-- Each child will have 1-2 sessions

-- Child 1 (Emma) - Session 1 (recent)
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics)
VALUES (1002, 1001, 3, '2025-02-04 11:42:49', true, false);

-- Child 2 (Liam) - Session 1 (recent)
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics)
VALUES (1003, 1002, 3, '2025-02-04 11:42:49', true, false);

-- Child 3 (Olivia) - Session 1 (recent)
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics)
VALUES (1005, 1003, 3, '2025-02-04 11:42:49', false, false);

-- Child 3 (Olivia) - Session 2 (older)
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics)
VALUES (1006, 1003, 3, '2025-01-04 11:42:49', true, false);

-- Child 4 (Noah) - Session 1 (recent)
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics)
VALUES (1007, 1004, 4, '2025-02-04 11:42:49', true, false);

-- Child 6 (Ethan) - Session 1 (recent)
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics)
VALUES (1010, 1006, 5, '2025-02-04 11:42:49', false, false);

-- Child 7 (Sophia) - Session 1 (recent)
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics)
VALUES (1011, 1007, 5, '2025-02-04 11:42:49', false, false);

-- Child 7 (Sophia) - Session 2 (older)
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics)
VALUES (1012, 1007, 5, '2025-01-04 11:42:49', true, false);

-- Now add milestone answers for each session
-- Using milestone IDs 1000-1009 from importBaseMetadata.sql

-- Child 1 (Emma) - 3 months old - Session 1 (1002)
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1002, 1001, 1000, 0); -- Recognizing Colors (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1002, 1002, 1000, 0); -- Recognizing Letters (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1002, 1003, 1000, 0); -- Recognizing Digits (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1002, 1004, 1000, 0); -- Recognizing Words (not yet)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1002, 1005, 1001, 2); -- Moving to Music (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1002, 1008, 1001, 0); -- Following Dance Instructions (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1002, 1009, 1001, 0); -- Creating Dance Patterns (not yet)

-- Child 2 (Liam) - 8 months old - Session 1 (1003)
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1003, 1000, 1000, 3); -- Recognizing Shapes (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1003, 1001, 1000, 2); -- Recognizing Colors (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1003, 1004, 1000, 0); -- Recognizing Words (not yet)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1003, 1005, 1001, 3); -- Moving to Music (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1003, 1008, 1001, 0); -- Following Dance Instructions (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1003, 1009, 1001, 0); -- Creating Dance Patterns (not yet)

-- Child 2 (Liam) - 8 months old - Session 2 (1004) - older session
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1004, 1000, 1000, 2); -- Recognizing Shapes (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1004, 1001, 1000, 1); -- Recognizing Colors (beginning)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1004, 1002, 1000, 0); -- Recognizing Letters (not yet)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1004, 1005, 1001, 2); -- Moving to Music (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1004, 1006, 1001, 1); -- Clapping Hands (beginning)


INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1004, 1009, 1001, 0); -- Creating Dance Patterns (not yet)

-- Child 3 (Olivia) - 12 months old - Session 1 (1005)
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1005, 1000, 1000, 3); -- Recognizing Shapes (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1005, 1001, 1000, 3); -- Recognizing Colors (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1005, 1004, 1000, 0); -- Recognizing Words (not yet)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1005, 1005, 1001, 3); -- Moving to Music (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1005, 1006, 1001, 3); -- Clapping Hands (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1005, 1009, 1001, 0); -- Creating Dance Patterns (not yet)

-- Child 3 (Olivia) - 12 months old - Session 2 (1006) - older session
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1006, 1000, 1000, 2); -- Recognizing Shapes (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1006, 1002, 1000, 1); -- Recognizing Letters (beginning)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1006, 1003, 1000, 0); -- Recognizing Digits (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1006, 1004, 1000, 0); -- Recognizing Words (not yet)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1006, 1006, 1001, 2); -- Clapping Hands (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1006, 1007, 1001, 1); -- Simple Dance Moves (beginning)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1006, 1008, 1001, 0); -- Following Dance Instructions (not yet)

-- Child 4 (Noah) - 18 months old - Session 1 (1007)
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1000, 1000, 3); -- Recognizing Shapes (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1001, 1000, 3); -- Recognizing Colors (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1002, 1000, 3); -- Recognizing Letters (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1003, 1000, 2); -- Recognizing Digits (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1004, 1000, 1); -- Recognizing Words (beginning)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1005, 1001, 3); -- Moving to Music (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1006, 1001, 3); -- Clapping Hands (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1007, 1001, 3); -- Simple Dance Moves (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1008, 1001, 2); -- Following Dance Instructions (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1007, 1009, 1001, 1); -- Creating Dance Patterns (beginning)

-- Child 5 (Ava) - 24 months old - Session 1 (1008)
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1000, 1000, 3); -- Recognizing Shapes (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1001, 1000, 3); -- Recognizing Colors (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1002, 1000, 3); -- Recognizing Letters (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1003, 1000, 3); -- Recognizing Digits (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1004, 1000, 2); -- Recognizing Words (sometimes)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1005, 1001, 3); -- Moving to Music (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1006, 1001, 3); -- Clapping Hands (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1007, 1001, 3); -- Simple Dance Moves (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1008, 1001, 3); -- Following Dance Instructions (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1008, 1009, 1001, 2); -- Creating Dance Patterns (sometimes)

-- Child 5 (Ava) - 24 months old - Session 2 (1009) - older session
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1009, 1000, 1000, 3); -- Recognizing Shapes (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1009, 1001, 1000, 3); -- Recognizing Colors (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1009, 1002, 1000, 2); -- Recognizing Letters (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1009, 1003, 1000, 2); -- Recognizing Digits (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1009, 1004, 1000, 1); -- Recognizing Words (beginning)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1009, 1005, 1001, 3); -- Moving to Music (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1009, 1006, 1001, 3); -- Clapping Hands (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1009, 1009, 1001, 1); -- Creating Dance Patterns (beginning)

-- Child 6 (Ethan) - 30 months old - Session 1 (1010)
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1010, 1000, 1000, 3); -- Recognizing Shapes (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1010, 1001, 1000, 3); -- Recognizing Colors (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1010, 1002, 1000, 3); -- Recognizing Letters (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1010, 1003, 1000, 3); -- Recognizing Digits (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1010, 1004, 1000, 3); -- Recognizing Words (fully achieved)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1010, 1005, 1001, 3); -- Moving to Music (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1010, 1008, 1001, 3); -- Following Dance Instructions (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1010, 1009, 1001, 3); -- Creating Dance Patterns (fully achieved)

-- Child 7 (Sophia) - 36 months old - Session 1 (1011)
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1011, 1000, 1000, 3); -- Recognizing Shapes (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1011, 1001, 1000, 3); -- Recognizing Colors (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1011, 1004, 1000, 3); -- Recognizing Words (fully achieved)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1011, 1005, 1001, 3); -- Moving to Music (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1011, 1006, 1001, 3); -- Clapping Hands (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1011, 1007, 1001, 3); -- Simple Dance Moves (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1011, 1009, 1001, 3); -- Creating Dance Patterns (fully achieved)

-- Child 7 (Sophia) - 36 months old - Session 2 (1012) - older session
-- Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1012, 1000, 1000, 3); -- Recognizing Shapes (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1012, 1001, 1000, 3); -- Recognizing Colors (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1012, 1002, 1000, 3); -- Recognizing Letters (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1012, 1004, 1000, 2); -- Recognizing Words (sometimes)

-- Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1012, 1005, 1001, 3); -- Moving to Music (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1012, 1009, 1001, 2); -- Creating Dance Patterns (sometimes)
