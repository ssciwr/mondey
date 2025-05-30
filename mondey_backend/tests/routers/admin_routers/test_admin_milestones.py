import datetime
import pathlib

import pytest
from dateutil.relativedelta import relativedelta
from fastapi.testclient import TestClient
from PIL import Image

from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import SuspiciousState
from mondey_backend.routers.utils import count_milestone_answers_for_milestone


def test_get_milestone_groups(
    admin_client: TestClient, milestone_group_admin1: dict, milestone_group_admin2: dict
):
    response = admin_client.get("/admin/milestone-groups/")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json() == [milestone_group_admin2, milestone_group_admin1]


def test_post_milestone_group(admin_client: TestClient):
    response = admin_client.post("/admin/milestone-groups/")
    assert response.status_code == 200
    assert response.json() == {
        "id": 3,
        "order": 0,
        "text": {
            "de": {
                "group_id": 3,
                "lang_id": "de",
                "title": "",
                "desc": "",
            },
            "en": {
                "group_id": 3,
                "lang_id": "en",
                "title": "",
                "desc": "",
            },
            "fr": {
                "group_id": 3,
                "lang_id": "fr",
                "title": "",
                "desc": "",
            },
        },
        "milestones": [],
    }


def test_put_milestone_group(admin_client: TestClient, milestone_group_admin1: dict):
    milestone_group = milestone_group_admin1
    milestone_group["order"] = 6
    milestone_group["text"]["de"]["title"] = "asdsd"
    milestone_group["text"]["de"]["desc"] = "12xzascdasdf"
    milestone_group["text"]["en"]["title"] = "asqwdreqweqw"
    milestone_group["text"]["en"]["desc"] = "th567"
    response = admin_client.put("/admin/milestone-groups", json=milestone_group)
    assert response.status_code == 200
    assert response.json() == milestone_group


def test_delete_milestone_group_invalid_group_id(admin_client: TestClient):
    response = admin_client.delete("/admin/milestone-groups/692?dry_run=false")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "endpoint",
    ["/admin/languages/fr", "/admin/milestone-groups/1", "/admin/milestones/1"],
)
@pytest.mark.parametrize(
    "client_type", ["public_client", "user_client", "research_client"]
)
def test_delete_endpoints_invalid_admin_user(
    endpoint: str, client_type: str, request: pytest.FixtureRequest
):
    client = request.getfixturevalue(client_type)
    response = client.delete(endpoint)
    assert response.status_code == 401


@pytest.mark.parametrize(
    ["image_path_fixture", "image_tag"],
    [
        ("image_file_jpg_1600_1200", "image/jpeg"),
        ("image_file_jpg_64_64", "image/jpeg"),
        ("image_file_png_1100_1100", "image/png"),
    ],
)
def test_put_milestone_group_image(
    admin_client: TestClient,
    static_dir: pathlib.Path,
    image_path_fixture: str,
    image_tag: str,
    request: pytest.FixtureRequest,
):
    image_path = request.getfixturevalue(image_path_fixture)
    static_dir_image_file = static_dir / "mg" / "1.webp"
    assert not static_dir_image_file.is_file()
    original_width = Image.open(image_path).size[0]
    with open(image_path, "rb") as f:
        response = admin_client.put(
            "/admin/milestone-group-images/1",
            files={"file": ("filename", f, image_tag)},
        )
    assert response.status_code == 200
    assert static_dir_image_file.is_file()
    assert Image.open(static_dir_image_file).size[0] == min(original_width, 1024)


def test_post_milestone(admin_client: TestClient):
    response = admin_client.post("/admin/milestones/2")
    assert response.status_code == 200
    assert response.json() == {
        "id": 6,
        "name": "",
        "group_id": 2,
        "order": 0,
        "expected_age_months": 12,
        "expected_age_delta": 6,
        "text": {
            "de": {
                "milestone_id": 6,
                "lang_id": "de",
                "title": "",
                "desc": "",
                "obs": "",
                "help": "",
            },
            "en": {
                "milestone_id": 6,
                "lang_id": "en",
                "title": "",
                "desc": "",
                "obs": "",
                "help": "",
            },
            "fr": {
                "milestone_id": 6,
                "lang_id": "fr",
                "title": "",
                "desc": "",
                "obs": "",
                "help": "",
            },
        },
        "images": [],
    }


def test_put_milestone(admin_client: TestClient, milestone_group_admin1: dict):
    milestone = milestone_group_admin1["milestones"][0]
    assert milestone["id"] == 3
    # create a new ~6 year child & check that they don't see the milestone 3 in their answer session
    create_child = {
        "name": "new child",
        "birth_year": datetime.datetime.now().year - 6,
        "birth_month": 3,
        "color": "#000000",
    }
    new_child_id = admin_client.post("/users/children/", json=create_child).json()["id"]
    response = admin_client.get(f"/milestone-groups/{new_child_id}")
    milestone_ids = [m["id"] for group in response.json() for m in group["milestones"]]
    assert 3 not in milestone_ids
    # modify a milestone such that a 6 year old child should now see it in their milestone answer session
    milestone["name"] = "bob"
    milestone["order"] = 6
    milestone["expected_age_months"] = 11
    milestone["expected_age_delta"] = 99
    milestone["text"]["de"]["title"] = "asdsd"
    milestone["text"]["de"]["desc"] = "12xzascdasdf"
    milestone["text"]["de"]["obs"] = "asdrgf"
    milestone["text"]["de"]["help"] = "jgfhj"
    milestone["text"]["en"]["title"] = "asqwdreqweqw"
    milestone["text"]["en"]["desc"] = "th567"
    response = admin_client.put("/admin/milestones", json=milestone)
    assert response.status_code == 200
    assert response.json() == milestone
    # check that a child of this age now sees milestone 3 in their milestone answer session
    new_child_id = admin_client.post("/users/children/", json=create_child).json()["id"]
    response = admin_client.get(f"/milestone-groups/{new_child_id}")
    milestone_ids = [m["id"] for group in response.json() for m in group["milestones"]]
    assert 3 in milestone_ids


def test_delete_milestone(admin_client: TestClient):
    assert admin_client.get("/milestones/2").status_code == 200
    response = admin_client.delete("/admin/milestones/2?dry_run=false")
    assert response.status_code == 200
    assert admin_client.get("/milestones/2").status_code == 404
    response = admin_client.delete("/admin/milestones/2?dry_run=false")
    assert response.status_code == 404


def test_post_milestone_image(
    admin_client: TestClient,
    static_dir: pathlib.Path,
    image_file_jpg_1600_1200: pathlib.Path,
):
    # 3 milestone images already exist
    assert len(admin_client.get("/milestones/1").json()["images"]) == 2
    assert len(admin_client.get("/milestones/2").json()["images"]) == 1
    assert len(admin_client.get("/milestones/3").json()["images"]) == 0
    assert len(admin_client.get("/milestones/4").json()["images"]) == 0
    assert len(admin_client.get("/milestones/5").json()["images"]) == 0
    # image ids are sequential
    milestone_image_id = 3
    # add an image to each milestone
    for milestone_id in [1, 2, 3, 4, 5]:
        milestone_image_id += 1
        filename = f"{milestone_image_id}.webp"
        static_dir_image_file = static_dir / "m" / filename
        assert not static_dir_image_file.is_file()
        with open(image_file_jpg_1600_1200, "rb") as f:
            response = admin_client.post(
                f"/admin/milestone-images/{milestone_id}",
                files={"file": ("filename", f, "image/jpeg")},
            )
        assert response.status_code == 200
        assert static_dir_image_file.is_file()
    assert len(admin_client.get("/milestones/1").json()["images"]) == 3
    assert len(admin_client.get("/milestones/2").json()["images"]) == 2
    assert len(admin_client.get("/milestones/3").json()["images"]) == 1
    assert len(admin_client.get("/milestones/4").json()["images"]) == 1
    assert len(admin_client.get("/milestones/5").json()["images"]) == 1
    # remove added images
    for milestone_image_id in range(4, 9):
        filename = f"{milestone_image_id}.webp"
        static_dir_image_file = static_dir / "m" / filename
        assert static_dir_image_file.is_file()
        assert (
            admin_client.delete(
                f"/admin/milestone-images/{milestone_image_id}"
            ).status_code
            == 200
        )
        assert not static_dir_image_file.is_file()
    assert len(admin_client.get("/milestones/1").json()["images"]) == 2
    assert len(admin_client.get("/milestones/2").json()["images"]) == 1
    assert len(admin_client.get("/milestones/3").json()["images"]) == 0
    assert len(admin_client.get("/milestones/4").json()["images"]) == 0
    assert len(admin_client.get("/milestones/5").json()["images"]) == 0


def test_get_milestone_age_scores(admin_client: TestClient):
    response = admin_client.get("/admin/milestone-age-scores/1")
    assert response.status_code == 200

    assert response.json()["expected_age"] == 8
    assert response.json()["expected_age_delta"] == 4

    assert response.json()["scores"][7]["avg_score"] == pytest.approx(0.0)
    assert response.json()["scores"][7]["stddev_score"] == pytest.approx(0.0)
    assert response.json()["scores"][7]["count"] == 0

    assert response.json()["scores"][8]["avg_score"] == pytest.approx(1.0)
    assert response.json()["scores"][8]["stddev_score"] == pytest.approx(0.0)
    assert response.json()["scores"][8]["count"] == 1

    assert response.json()["scores"][9]["avg_score"] == pytest.approx(0.0)
    assert response.json()["scores"][9]["stddev_score"] == pytest.approx(0.0)
    assert response.json()["scores"][9]["count"] == 0


def test_get_submitted_milestone_images(admin_client: TestClient):
    response = admin_client.get("/admin/submitted-milestone-images")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_approve_submitted_milestone_image(
    admin_client: TestClient,
    static_dir: pathlib.Path,
):
    submitted_image_file = static_dir / "ms" / "1.webp"
    assert submitted_image_file.is_file()
    approved_image_file = static_dir / "m" / "4.webp"
    assert not approved_image_file.is_file()
    assert len(admin_client.get("/admin/submitted-milestone-images").json()) == 2
    response = admin_client.post("/admin/submitted-milestone-images/approve/1")
    assert response.status_code == 200
    assert not submitted_image_file.is_file()
    assert approved_image_file.is_file()
    assert len(admin_client.get("/admin/submitted-milestone-images").json()) == 1


def test_delete_submitted_milestone_image(
    admin_client: TestClient,
    static_dir: pathlib.Path,
):
    submitted_image_file = static_dir / "ms" / "1.webp"
    assert submitted_image_file.is_file()
    approved_image_file = static_dir / "m" / "4.webp"
    assert not approved_image_file.is_file()
    assert len(admin_client.get("/admin/submitted-milestone-images").json()) == 2
    response = admin_client.delete("/admin/submitted-milestone-images/1")
    assert response.status_code == 200
    assert not submitted_image_file.is_file()
    assert not approved_image_file.is_file()
    assert len(admin_client.get("/admin/submitted-milestone-images").json()) == 1


"""
Test that deleting a milestone actually deletes nothing (count milestone answers remains the same) with dry_run = True
or non-specified dry_run value, and that deleting a milestone with dry_run = False succeeds
"""


def test_delete_milestone_dry_run(admin_client, session):
    milestone_id = 2
    expected_answers_from_fixtures = 4  # Has these 3 existing answers in the fixtures.
    assert (
        count_milestone_answers_for_milestone(session, milestone_id)
        == expected_answers_from_fixtures
    )

    # Fake delete call without dry run param at all (should default to dry run to be safe)
    response = admin_client.delete(f"/admin/milestones/{milestone_id}")
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["dry_run"]
    assert "children" in response_json
    assert (
        response_json["children"]["affectedAnswers"] == expected_answers_from_fixtures
    )
    assert (
        count_milestone_answers_for_milestone(session, milestone_id)
        == expected_answers_from_fixtures
    )

    # Fake delete call with explicit dry_run param set to True
    response = admin_client.delete(f"/admin/milestones/{milestone_id}?dry_run=true")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["dry_run"]
    assert "children" in response_json
    assert (
        response_json["children"]["affectedAnswers"] == expected_answers_from_fixtures
    )
    assert (
        count_milestone_answers_for_milestone(session, milestone_id)
        == expected_answers_from_fixtures
    )


def test_delete_milestone_confirmed(admin_client, session):
    milestone_id = 2
    expected_answers_from_fixtures = 4  # Has these 3 existing answers in the fixtures.
    assert (
        count_milestone_answers_for_milestone(session, milestone_id)
        == expected_answers_from_fixtures
    )

    # Real delete call with dry_run param set to False
    response = admin_client.delete(f"/admin/milestones/{milestone_id}?dry_run=false")
    assert response.status_code == 200
    assert response.json()["ok"]
    assert count_milestone_answers_for_milestone(session, milestone_id) == 0


## Test Delete whole milestone groups:
def test_delete_milestone_groups_dry_run(admin_client, session):
    milestone_group_id = 1  # owns milestones 1, 2, 3
    milestone_id_to_answer_count = {1: 4, 2: 4, 3: 0}
    for milestone_id, num_answers in milestone_id_to_answer_count.items():
        assert (
            count_milestone_answers_for_milestone(session, milestone_id) == num_answers
        )

    # Fake delete call without dry run param at all (should default to dry run to be safe)
    response = admin_client.delete(f"/admin/milestone-groups/{milestone_group_id}")
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["dry_run"]
    assert "children" in response_json
    assert response_json["children"]["affectedAnswers"] == sum(
        milestone_id_to_answer_count.values()
    )
    assert response_json["children"]["affectedMilestones"] == len(
        milestone_id_to_answer_count
    )

    response = admin_client.delete(f"/admin/milestone-groups/{milestone_group_id}")
    assert response.status_code == 200  # still exists because was dry run.


## Test Delete whole milestone groups:
def test_delete_milestone_groups_real(admin_client, session):
    milestone_group_id = 1  # owns milestones 1, 2, 3
    milestone_id_to_answer_count = {1: 4, 2: 4, 3: 0}
    for milestone_id, num_answers in milestone_id_to_answer_count.items():
        assert (
            count_milestone_answers_for_milestone(session, milestone_id) == num_answers
        )

    # Fake delete call without dry run param at all (should default to dry run to be safe)
    response = admin_client.delete(
        f"/admin/milestone-groups/{milestone_group_id}?dry_run=false"
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["ok"]
    assert response_json["children"]["affectedMilestones"] == 3
    assert response_json["children"]["affectedAnswers"] == sum(
        milestone_id_to_answer_count.values()
    )

    for milestone_id in milestone_id_to_answer_count:
        assert count_milestone_answers_for_milestone(session, milestone_id) == 0
    response = admin_client.delete(
        f"/admin/milestone-groups/{milestone_group_id}?dry_run=false"
    )
    assert response.status_code == 404  # gone for good, because was real, not dry_run.


def test_get_milestone_answer_sessions(admin_client: TestClient, session):
    # update the stats
    assert admin_client.post("/admin/update-stats/true").status_code == 200
    response = admin_client.get("/admin/milestone-answer-sessions/")
    assert response.status_code == 200
    answer_sessions = response.json()
    # all 7 answer sessions should be returned
    assert len(answer_sessions) == 7
    for answer_session in answer_sessions:
        # none of them are marked as suspicious
        assert answer_session["suspicious_state"] == SuspiciousState.not_suspicious
    # add a completed answer session with answers that should be flagged as suspicious
    today = datetime.datetime.today()
    last_month = today - relativedelta(months=1)
    session.add(
        MilestoneAnswerSession(
            id=666,
            child_id=1,
            user_id=3,
            created_at=datetime.datetime(
                last_month.year, last_month.month, last_month.day
            ),
            expired=True,
            completed=True,
            included_in_statistics=False,
            suspicious_state=SuspiciousState.not_suspicious,
        )
    )
    session.add(
        MilestoneAnswer(
            answer_session_id=666, milestone_id=1, milestone_group_id=1, answer=3
        )
    )
    session.add(
        MilestoneAnswer(
            answer_session_id=666, milestone_id=2, milestone_group_id=1, answer=3
        )
    )
    # the new answer session is initially not marked as suspicious and is not included in the statistics
    new_answer_sessions = admin_client.get("/admin/milestone-answer-sessions/").json()
    assert len(new_answer_sessions) == 8
    assert new_answer_sessions[-1]["id"] == 666
    assert new_answer_sessions[-1]["suspicious_state"] == SuspiciousState.not_suspicious
    assert not new_answer_sessions[-1]["included_in_statistics"]
    # after running an incremental stats update, the new answer session should be marked as suspicious & remain not included in statistics
    assert admin_client.post("/admin/update-stats/true").status_code == 200
    new_answer_sessions = admin_client.get("/admin/milestone-answer-sessions/").json()
    assert len(new_answer_sessions) == 8
    assert new_answer_sessions[-1]["id"] == 666
    assert new_answer_sessions[-1]["suspicious_state"] == SuspiciousState.suspicious
    assert not new_answer_sessions[-1]["included_in_statistics"]


def test_modify_milestone_answer_session(admin_client: TestClient):
    assert (
        admin_client.get("/admin/milestone-answer-sessions/").json()[0][
            "suspicious_state"
        ]
        == SuspiciousState.not_suspicious
    )
    response = admin_client.post("/admin/milestone-answer-sessions/1?suspicious=true")
    assert response.status_code == 200
    assert (
        admin_client.get("/admin/milestone-answer-sessions/").json()[0][
            "suspicious_state"
        ]
        == SuspiciousState.admin_suspicious
    )

    # now it should be explicitly not suspicious by admins command...
    response = admin_client.post("/admin/milestone-answer-sessions/1?suspicious=false")
    assert response.status_code == 200
    assert (
        admin_client.get("/admin/milestone-answer-sessions/").json()[0][
            "suspicious_state"
        ]
        == SuspiciousState.admin_not_suspicious
    )


# A test because the enum SuspiciousState has 4 values depending on whether the admin has manually overriden the "suspicious-detection".
def test_modify_milestone_answer_session_to_admin_set_non_suspicious_first(
    admin_client: TestClient,
):
    assert (
        admin_client.get("/admin/milestone-answer-sessions/").json()[0][
            "suspicious_state"
        ]
        == SuspiciousState.not_suspicious
    )
    response = admin_client.post("/admin/milestone-answer-sessions/1?suspicious=false")
    assert response.status_code == 200
    assert (
        admin_client.get("/admin/milestone-answer-sessions/").json()[0][
            "suspicious_state"
        ]
        == SuspiciousState.admin_not_suspicious
    )


def test_modify_milestone_answer_session_does_not_exist(admin_client: TestClient):
    response = admin_client.post(
        "/admin/milestone-answer-sessions/7942?suspicious=true"
    )
    assert response.status_code == 404


def test_get_milestone_answer_session_analysis(admin_client: TestClient):
    response = admin_client.get("/admin/milestone-answer-session-analysis/1")
    assert response.status_code == 200
    analysis = response.json()
    assert len(analysis["answers"]) == 2
    assert analysis["answers"][0]["milestone_id"] == 1
    assert analysis["answers"][0]["answer"] == 1
    assert analysis["answers"][0]["avg_answer"] == pytest.approx(1.0)
    assert analysis["answers"][1]["milestone_id"] == 2
    assert analysis["answers"][1]["answer"] == 0
    assert analysis["answers"][1]["avg_answer"] == pytest.approx(0.0)
    # rms = sqrt(((1-1)^2 + (0-0)^2) / 2) = 0
    assert analysis["rms"] == pytest.approx(0.0)
    assert analysis["child_age"] == 8


def test_get_milestone_answer_session_analysis_no_stats(admin_client: TestClient):
    # milestone 5 doesn't have any statistics yet
    response = admin_client.get("/admin/milestone-answer-session-analysis/3")
    assert response.status_code == 200
    analysis = response.json()
    assert len(analysis["answers"]) == 0
    assert analysis["rms"] == pytest.approx(0.0)
    assert 50 < analysis["child_age"] < 60
    # update stats
    assert admin_client.post("/admin/update-stats/false").status_code == 200
    # now we get analysis for the milestones in this answer session
    response = admin_client.get("/admin/milestone-answer-session-analysis/3")
    assert response.status_code == 200
    analysis = response.json()
    assert len(analysis["answers"]) == 1
    assert analysis["answers"][0]["milestone_id"] == 5
    assert analysis["answers"][0]["answer"] == 2
    assert analysis["answers"][0]["avg_answer"] == pytest.approx(2.0)
    assert analysis["rms"] == pytest.approx(0.0)
    assert 50 < analysis["child_age"] < 60


def test_get_milestone_answer_session_analysis_no_answer_session(
    admin_client: TestClient,
):
    # this milestone answer session doesn't exist
    assert (
        admin_client.get("/admin/milestone-answer-session-analysis/348").status_code
        == 404
    )
