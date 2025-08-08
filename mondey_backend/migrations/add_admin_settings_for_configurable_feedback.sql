CREATE TABLE adminsettings (
    id INTEGER NOT NULL,
    hide_milestone_feedback BOOLEAN NOT NULL,
    hide_milestone_group_feedback BOOLEAN NOT NULL,
    hide_all_feedback BOOLEAN NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO adminsettings (id, hide_milestone_feedback, hide_milestone_group_feedback, hide_all_feedback)
VALUES (1, false, false, false);
