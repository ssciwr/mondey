-- Add milestone groups
INSERT INTO milestonegroup (id, "order") VALUES (1000, 1);
INSERT INTO milestonegroup (id, "order") VALUES (1001, 2);

-- Add milestone group texts
-- Reading Text group
INSERT INTO milestonegrouptext (group_id, lang_id, title, desc)
VALUES (1000, 'en', 'Reading Text', 'Skills related to reading and text recognition');
INSERT INTO milestonegrouptext (group_id, lang_id, title, desc)
VALUES (1000, 'de', 'Textlesen', 'Fähigkeiten im Zusammenhang mit Lesen und Texterkennung');
INSERT INTO milestonegrouptext (group_id, lang_id, title, desc)
VALUES (1000, 'fr', 'Lecture de texte', 'Compétences liées à la lecture et à la reconnaissance de texte');

-- Dancing Skills group
INSERT INTO milestonegrouptext (group_id, lang_id, title, desc)
VALUES (1001, 'en', 'Dancing Skills', 'Skills related to movement and dancing');
INSERT INTO milestonegrouptext (group_id, lang_id, title, desc)
VALUES (1001, 'de', 'Tanzfähigkeiten', 'Fähigkeiten im Zusammenhang mit Bewegung und Tanzen');
INSERT INTO milestonegrouptext (group_id, lang_id, title, desc)
VALUES (1001, 'fr', 'Compétences en danse', 'Compétences liées au mouvement et à la danse');

-- Add milestones for Reading Text group
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1000, 1000, 1, 3, 'Recognizing Shapes');
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1001, 1000, 2, 6, 'Recognizing Colors');
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1002, 1000, 3, 9, 'Recognizing Letters');
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1003, 1000, 4, 12, 'Recognizing Digits');
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1004, 1000, 5, 18, 'Recognizing Words');

-- Add milestones for Dancing Skills group
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1005, 1001, 1, 3, 'Moving to Music');
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1006, 1001, 2, 6, 'Clapping Hands');
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1007, 1001, 3, 9, 'Simple Dance Moves');
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1008, 1001, 4, 12, 'Following Dance Instructions');
INSERT INTO milestone (id, group_id, "order", expected_age_months, name)
VALUES (1009, 1001, 5, 18, 'Creating Dance Patterns');

-- Add milestone texts for Reading Text group
-- Recognizing Shapes
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1000, 'en', 'Recognizing Shapes', 'Child can identify basic shapes like circles and squares', 'Observe if child points to shapes when asked', 'Show different shapes and ask child to identify them');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1000, 'de', 'Formen erkennen', 'Kind kann grundlegende Formen wie Kreise und Quadrate identifizieren', 'Beobachten Sie, ob das Kind auf Formen zeigt, wenn es danach gefragt wird', 'Zeigen Sie verschiedene Formen und bitten Sie das Kind, sie zu identifizieren');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1000, 'fr', 'Reconnaissance des formes', 'L''enfant peut identifier des formes de base comme des cercles et des carrés', 'Observez si l''enfant pointe vers des formes lorsqu''on le lui demande', 'Montrez différentes formes et demandez à l''enfant de les identifier');

-- Recognizing Colors
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1001, 'en', 'Recognizing Colors', 'Child can identify primary colors', 'Observe if child points to colors when asked', 'Show different colored objects and ask child to identify them');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1001, 'de', 'Farben erkennen', 'Kind kann Primärfarben identifizieren', 'Beobachten Sie, ob das Kind auf Farben zeigt, wenn es danach gefragt wird', 'Zeigen Sie verschiedenfarbige Objekte und bitten Sie das Kind, sie zu identifizieren');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1001, 'fr', 'Reconnaissance des couleurs', 'L''enfant peut identifier les couleurs primaires', 'Observez si l''enfant pointe vers des couleurs lorsqu''on le lui demande', 'Montrez des objets de différentes couleurs et demandez à l''enfant de les identifier');

-- Recognizing Letters
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1002, 'en', 'Recognizing Letters', 'Child can identify some letters of the alphabet', 'Observe if child points to letters when asked', 'Show different letters and ask child to identify them');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1002, 'de', 'Buchstaben erkennen', 'Kind kann einige Buchstaben des Alphabets identifizieren', 'Beobachten Sie, ob das Kind auf Buchstaben zeigt, wenn es danach gefragt wird', 'Zeigen Sie verschiedene Buchstaben und bitten Sie das Kind, sie zu identifizieren');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1002, 'fr', 'Reconnaissance des lettres', 'L''enfant peut identifier certaines lettres de l''alphabet', 'Observez si l''enfant pointe vers des lettres lorsqu''on le lui demande', 'Montrez différentes lettres et demandez à l''enfant de les identifier');

-- Recognizing Digits
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1003, 'en', 'Recognizing Digits', 'Child can identify some numbers', 'Observe if child points to numbers when asked', 'Show different numbers and ask child to identify them');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1003, 'de', 'Ziffern erkennen', 'Kind kann einige Zahlen identifizieren', 'Beobachten Sie, ob das Kind auf Zahlen zeigt, wenn es danach gefragt wird', 'Zeigen Sie verschiedene Zahlen und bitten Sie das Kind, sie zu identifizieren');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1003, 'fr', 'Reconnaissance des chiffres', 'L''enfant peut identifier certains chiffres', 'Observez si l''enfant pointe vers des chiffres lorsqu''on le lui demande', 'Montrez différents chiffres et demandez à l''enfant de les identifier');

-- Recognizing Words
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1004, 'en', 'Recognizing Words', 'Child can identify some simple words', 'Observe if child points to words when asked', 'Show different words and ask child to identify them');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1004, 'de', 'Wörter erkennen', 'Kind kann einige einfache Wörter identifizieren', 'Beobachten Sie, ob das Kind auf Wörter zeigt, wenn es danach gefragt wird', 'Zeigen Sie verschiedene Wörter und bitten Sie das Kind, sie zu identifizieren');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1004, 'fr', 'Reconnaissance des mots', 'L''enfant peut identifier certains mots simples', 'Observez si l''enfant pointe vers des mots lorsqu''on le lui demande', 'Montrez différents mots et demandez à l''enfant de les identifier');

-- Add milestone texts for Dancing Skills group
-- Moving to Music
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1005, 'en', 'Moving to Music', 'Child moves body in response to music', 'Observe if child reacts to music with movement', 'Play different types of music and observe reactions');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1005, 'de', 'Bewegung zur Musik', 'Kind bewegt den Körper als Reaktion auf Musik', 'Beobachten Sie, ob das Kind auf Musik mit Bewegung reagiert', 'Spielen Sie verschiedene Arten von Musik und beobachten Sie die Reaktionen');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1005, 'fr', 'Bouger en musique', 'L''enfant bouge son corps en réponse à la musique', 'Observez si l''enfant réagit à la musique par des mouvements', 'Jouez différents types de musique et observez les réactions');

-- Clapping Hands
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1006, 'en', 'Clapping Hands', 'Child can clap hands to rhythm', 'Observe if child attempts to clap along to music', 'Demonstrate clapping and encourage child to join');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1006, 'de', 'Händeklatschen', 'Kind kann im Rhythmus in die Hände klatschen', 'Beobachten Sie, ob das Kind versucht, zur Musik zu klatschen', 'Demonstrieren Sie das Klatschen und ermutigen Sie das Kind mitzumachen');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1006, 'fr', 'Taper des mains', 'L''enfant peut taper des mains au rythme', 'Observez si l''enfant essaie de taper des mains en suivant la musique', 'Démontrez le tapement des mains et encouragez l''enfant à se joindre');

-- Simple Dance Moves
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1007, 'en', 'Simple Dance Moves', 'Child can perform simple dance moves', 'Observe if child attempts to imitate dance moves', 'Demonstrate simple moves and encourage child to copy');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1007, 'de', 'Einfache Tanzbewegungen', 'Kind kann einfache Tanzbewegungen ausführen', 'Beobachten Sie, ob das Kind versucht, Tanzbewegungen nachzuahmen', 'Demonstrieren Sie einfache Bewegungen und ermutigen Sie das Kind, sie zu kopieren');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1007, 'fr', 'Mouvements de danse simples', 'L''enfant peut effectuer des mouvements de danse simples', 'Observez si l''enfant tente d''imiter des mouvements de danse', 'Démontrez des mouvements simples et encouragez l''enfant à les copier');

-- Following Dance Instructions
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1008, 'en', 'Following Dance Instructions', 'Child can follow simple dance instructions', 'Observe if child follows verbal dance instructions', 'Give simple instructions like "spin around" or "jump"');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1008, 'de', 'Tanzanweisungen folgen', 'Kind kann einfachen Tanzanweisungen folgen', 'Beobachten Sie, ob das Kind verbalen Tanzanweisungen folgt', 'Geben Sie einfache Anweisungen wie "dreh dich" oder "spring"');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1008, 'fr', 'Suivre des instructions de danse', 'L''enfant peut suivre des instructions de danse simples', 'Observez si l''enfant suit des instructions verbales de danse', 'Donnez des instructions simples comme "tourne" ou "saute"');

-- Creating Dance Patterns
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1009, 'en', 'Creating Dance Patterns', 'Child can create simple dance patterns', 'Observe if child creates own dance sequences', 'Encourage free dance and observe if patterns emerge');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1009, 'de', 'Tanzmuster erstellen', 'Kind kann einfache Tanzmuster erstellen', 'Beobachten Sie, ob das Kind eigene Tanzsequenzen erstellt', 'Ermutigen Sie zum freien Tanzen und beobachten Sie, ob Muster entstehen');
INSERT INTO milestonetext (milestone_id, lang_id, title, desc, obs, help)
VALUES (1009, 'fr', 'Création de motifs de danse', 'L''enfant peut créer des motifs de danse simples', 'Observez si l''enfant crée ses propres séquences de danse', 'Encouragez la danse libre et observez si des motifs émergent');

-- Create a child for user ID 1
INSERT INTO child (id, user_id, name, birth_year, birth_month, has_image, color)
VALUES(1,1,'userChild1',2024,12,0,'#402bde');

-- Create a child born 6 months ago for user ID 3
INSERT INTO child (id, user_id, name, birth_year, birth_month, has_image, color)
VALUES (1000, 3, 'Test Child',
        CASE
            WHEN strftime('%m', 'now') <= '06' THEN strftime('%Y', 'now') - 1
            ELSE strftime('%Y', 'now')
        END,
        CASE
            WHEN strftime('%m', 'now') <= '06' THEN strftime('%m', 'now') + 6
            ELSE strftime('%m', 'now') - 6
        END,
        false, '#f0f0ff');

-- Create milestone answer session for the child
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics, suspicious)
VALUES (1000, 1000, 3, datetime('now', '-1 day'), false, false, false);

-- Add answers for Reading Text milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1000, 1000, 3); -- Recognizing Shapes (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1001, 1000, 2); -- Recognizing Colors (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1002, 1000, 1); -- Recognizing Letters (beginning)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1003, 1000, 0); -- Recognizing Digits (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1004, 1000, 0); -- Recognizing Words (not yet)

-- Add answers for Dancing Skills milestones
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1005, 1001, 3); -- Moving to Music (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1006, 1001, 3); -- Clapping Hands (fully achieved)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1007, 1001, 2); -- Simple Dance Moves (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1008, 1001, 1); -- Following Dance Instructions (beginning)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1000, 1009, 1001, 0); -- Creating Dance Patterns (not yet)

-- Create a second milestone answer session from 2 months ago
INSERT INTO milestoneanswersession (id, child_id, user_id, created_at, expired, included_in_statistics, suspicious)
VALUES (1001, 1000, 3, datetime('now', '-2 months'), true, true, false);

-- Add answers for Reading Text milestones (previous session)
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1000, 1000, 2); -- Recognizing Shapes (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1001, 1000, 1); -- Recognizing Colors (beginning)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1002, 1000, 0); -- Recognizing Letters (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1003, 1000, 0); -- Recognizing Digits (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1004, 1000, 0); -- Recognizing Words (not yet)

-- Add answers for Dancing Skills milestones (previous session)
INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1005, 1001, 2); -- Moving to Music (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1006, 1001, 2); -- Clapping Hands (sometimes)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1007, 1001, 1); -- Simple Dance Moves (beginning)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1008, 1001, 0); -- Following Dance Instructions (not yet)

INSERT INTO milestoneanswer (answer_session_id, milestone_id, milestone_group_id, answer)
VALUES (1001, 1009, 1001, 0); -- Creating Dance Patterns (not yet)
