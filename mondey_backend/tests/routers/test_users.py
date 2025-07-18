import datetime
import pathlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlmodel import col

from mondey_backend.models.milestones import MilestoneAnswer
from mondey_backend.models.milestones import MilestoneAnswerSession
from mondey_backend.models.milestones import SuspiciousState
from mondey_backend.models.questions import ChildAnswer


def _is_approx_now(iso_date_string: str, delta=datetime.timedelta(hours=1)) -> bool:
    return (
        datetime.datetime.now() - datetime.datetime.fromisoformat(iso_date_string)
        < delta
    )


def test_get_child(
    user_client: TestClient, children: list[dict[str, str | bool | int]]
):
    response = user_client.get("/users/children/1")
    assert response.status_code == 200
    assert response.json() == children[0]


def test_get_child_fail(
    user_client: TestClient, children: list[dict[str, str | bool | int]]
):
    response = user_client.get("/users/children/605")
    assert response.status_code == 404


def test_get_children_of_user(
    user_client: TestClient, children: list[dict[str, str | bool | int]]
):
    response = user_client.get("/users/children/")
    assert response.status_code == 200
    assert len(response.json()) == 2
    for child, response_child in zip(children, response.json(), strict=False):
        for key, value in child.items():
            assert response_child[key] == value
        # both children have no active session
        # (child 1 answered all the milestones in their only session so it is completed, child 2 has no sessions at all)
        assert response.json()[0]["active_answer_session"] is False

    # create a new session for both children
    for child_id in [1, 2]:
        assert (
            user_client.get(f"/users/milestone-answers/{child_id}").status_code == 200
        )

    response = user_client.get("/users/children/")
    assert response.status_code == 200
    assert len(response.json()) == 2

    for child, response_child in zip(children, response.json(), strict=False):
        for key, value in child.items():
            assert response_child[key] == value
        # both children now have an active session with zero progress and approx 14 days remaining
        assert response.json()[0]["active_answer_session"] is True
        assert response.json()[0]["session_progress"] == pytest.approx(0.0)
        seconds_in_a_day = 60 * 60 * 24
        assert response.json()[0][
            "session_remaining_seconds"
        ] / seconds_in_a_day == pytest.approx(14)


def test_get_children_no_children(research_client: TestClient):
    response = research_client.get("/users/children/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_children_admin_user_1_child(
    admin_client: TestClient, children: list[dict[str, str | bool | int]]
):
    response = admin_client.get("/users/children/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    for key, value in children[2].items():
        assert response.json()[0][key] == value
    assert "session_progress" in response.json()[0]
    assert "active_answer_session" in response.json()[0]
    assert "session_remaining_seconds" in response.json()[0]


def test_get_children_invalid_user(public_client: TestClient):
    response = public_client.get("/users/children/")
    assert response.status_code == 401


def test_get_child_image(user_client: TestClient):
    response = user_client.get("/users/children-images/2")
    assert response.status_code == 200


def test_get_child_image_no_image(user_client: TestClient):
    response = user_client.get("/users/children-images/11")
    assert response.status_code == 404


expected_created_child = {
    "id": 5,
    "name": "new child",
    "birth_year": 2021,
    "birth_month": 3,
    "has_image": False,
    "color": "#000000",
}


def test_create_update_and_delete_child(user_client: TestClient):
    assert len(user_client.get("/users/children/").json()) == 2
    response_create = user_client.post(
        "/users/children/",
        json={
            "name": "new child",
            "birth_year": 2021,
            "birth_month": 3,
            "color": "#000000",
        },
    )
    assert response_create.status_code == 200
    assert response_create.json() == expected_created_child
    assert len(user_client.get("/users/children/").json()) == 3
    response_update = user_client.put(
        "/users/children/",
        json={
            "id": 5,
            "name": "c",
            "birth_year": 2020,
            "birth_month": 9,
            "has_image": False,
            "color": "af4413",
        },
    )
    assert response_update.status_code == 200
    assert response_update.json() == {
        "id": 5,
        "name": "c",
        "birth_year": 2020,
        "birth_month": 9,
        "has_image": False,
        "color": "af4413",
    }
    assert len(user_client.get("/users/children/").json()) == 3
    response_delete = user_client.delete("/users/children/5?dry_run=false")
    assert response_delete.status_code == 200
    assert len(user_client.get("/users/children/").json()) == 2


def test_create_future_child_fails(user_client: TestClient):
    assert len(user_client.get("/users/children/").json()) == 2
    response_create = user_client.post(
        "/users/children/",
        json={
            "name": "new child with future birth date",
            "birth_year": 2099,
            "birth_month": 3,
            "color": "#000000",
        },
    )
    assert response_create.status_code == 400
    assert len(user_client.get("/users/children/").json()) == 2


def test_delete_dry_run_does_not_delete_child(user_client: TestClient):
    assert len(user_client.get("/users/children/").json()) == 2
    response_create = user_client.post(
        "/users/children/",
        json={
            "name": "new child",
            "birth_year": 2021,
            "birth_month": 3,
            "color": "#000000",
        },
    )
    assert response_create.status_code == 200
    assert response_create.json() == expected_created_child

    assert len(user_client.get("/users/children/").json()) == 3  # will be a dry run
    response_delete = user_client.delete("/users/children/5")
    assert response_delete.status_code == 200
    assert len(user_client.get("/users/children/").json()) == 3


def test_delete_child_removes_answering_sessions(session, user_client: TestClient):
    assert len(user_client.get("/users/children/").json()) == 2

    # Count initial MilestoneAnswerSessions
    initial_sessions_stmt = select(MilestoneAnswerSession)
    initial_sessions_count = len(session.exec(initial_sessions_stmt).all())

    response_create = user_client.post(
        "/users/children/",
        json={
            "name": "new child",
            "birth_year": 2021,
            "birth_month": 3,
            "color": "#000000",
        },
    )
    assert response_create.status_code == 200
    new_child_id = 5
    assert response_create.json() == {
        "id": new_child_id,
        "name": "new child",
        "birth_year": 2021,
        "birth_month": 3,
        "has_image": False,
        "color": "#000000",
    }

    child_sessions_stmt = select(MilestoneAnswerSession).where(
        col(MilestoneAnswerSession.child_id) == new_child_id
    )
    child_sessions = session.exec(child_sessions_stmt).all()
    assert len(child_sessions) == 0

    # Create a MilestoneAnswerSession for the new child
    milestone_answer_session = MilestoneAnswerSession(
        child_id=new_child_id,
        user_id=1,
        expired=False,
        completed=False,
        included_in_statistics=True,
        suspicious_state=SuspiciousState.not_suspicious,
    )
    session.add(milestone_answer_session)
    session.flush()

    # Add a MilestoneAnswer to the session
    milestone_answer = MilestoneAnswer(
        answer_session_id=milestone_answer_session.id,
        milestone_id=1,
        milestone_group_id=1,
        answer=2,
    )
    session.add(milestone_answer)
    session.flush()

    child_question_answer = ChildAnswer(
        child_id=new_child_id, question_id=1, answer="FakeAnswer"
    )

    session.add(child_question_answer)
    session.commit()

    # Verify milestone answer session was created
    child_sessions_stmt = select(MilestoneAnswerSession).where(
        col(MilestoneAnswerSession.child_id) == new_child_id
    )
    child_sessions = session.exec(child_sessions_stmt).all()
    assert len(child_sessions) == 1

    # Verify total milestone sessions increased by 1
    after_create_sessions_stmt = select(MilestoneAnswerSession)
    after_create_sessions_count = len(session.exec(after_create_sessions_stmt).all())
    assert after_create_sessions_count == initial_sessions_count + 1

    child_answer = select(ChildAnswer).where(col(ChildAnswer.child_id) == new_child_id)
    child_answers = session.exec(child_answer).all()
    assert len(child_answers) == 1

    # dry run case:
    response_delete = user_client.delete(f"/users/children/{new_child_id}")
    assert response_delete.status_code == 200
    assert len(user_client.get("/users/children/").json()) == 3

    deleted_child_sessions = session.exec(child_sessions_stmt).all()
    assert len(deleted_child_sessions) == 1

    # Attempt to delete the child
    response_delete = user_client.delete(
        f"/users/children/{new_child_id}?dry_run=false"
    )
    assert response_delete.json()["ok"]
    assert len(user_client.get("/users/children/").json()) == 2

    # Check that milestone answer sessions for this child have been deleted now
    deleted_child_sessions = session.exec(child_sessions_stmt).all()
    assert len(deleted_child_sessions) == 0

    # Check that child answers were also deleted:
    child_answers = session.exec(child_answer).all()
    assert len(child_answers) == 0

    # Verify total milestone sessions decreased by 1
    after_delete_sessions_stmt = select(MilestoneAnswerSession)
    after_delete_sessions_count = len(session.exec(after_delete_sessions_stmt).all())
    assert after_delete_sessions_count == initial_sessions_count


def test_upload_child_image(
    user_client: TestClient,
    private_dir: pathlib.Path,
    image_file_jpg_1600_1200: pathlib.Path,
):
    private_dir_image_file = private_dir / "children" / "1.webp"
    # child 1 does not have an image:
    assert not private_dir_image_file.is_file()
    assert user_client.get("/users/children/").json()[0]["has_image"] is False
    assert user_client.get("/users/children-images/1").status_code == 404

    # add an image for the first child
    with open(image_file_jpg_1600_1200, "rb") as f:
        response = user_client.put(
            "/users/children-images/1",
            files={"file": ("filename", f, "image/jpeg")},
        )
    assert response.status_code == 200
    assert private_dir_image_file.is_file()
    assert user_client.get("/users/children/").json()[0]["has_image"] is True
    assert user_client.get("/users/children-images/1").status_code == 200


def test_delete_child_image(
    user_client: TestClient,
    private_dir: pathlib.Path,
    image_file_png_1100_1100: pathlib.Path,
):
    children_dir = private_dir / "children"
    # add an image for the first child
    with open(image_file_png_1100_1100, "rb") as f:
        response = user_client.put(
            "/users/children-images/1",
            files={"file": ("filename", f, "image/png")},
        )

    # delete the image
    response = user_client.delete("/users/children-images/1")
    assert response.status_code == 200
    assert not (children_dir / "1.jpg").is_file()
    assert user_client.get("/users/children/").json()[0]["has_image"] is False
    assert user_client.get("/users/children-images/1").status_code == 404


def test_get_milestone_answers_child1_user_does_not_own_child(user_client2: TestClient):
    response = user_client2.get("/users/milestone-answers/1")
    assert response.status_code == 404


def test_get_milestone_answers_child8_child_does_not_exist(admin_client: TestClient):
    response = admin_client.get("/users/milestone-answers/8")
    assert response.status_code == 404


def test_get_milestone_answers_child3_current_answer_session(
    admin_client: TestClient,
):
    response = admin_client.get("/users/milestone-answers/3")
    assert response.status_code == 200
    assert response.json()["id"] == 6
    assert response.json()["child_id"] == 3
    assert response.json()["answers"] == {
        "5": {
            "milestone_id": 5,
            "answer": -1,
        },
    }
    assert _is_approx_now(response.json()["created_at"])


def test_get_milestone_answers_child1_no_current_answer_session(
    user_client: TestClient,
):
    response = user_client.get("/users/milestone-answers/1")
    assert response.status_code == 200
    assert response.json()["child_id"] == 1
    assert _is_approx_now(response.json()["created_at"])
    assert response.json()["answers"] == {
        "1": {
            "milestone_id": 1,
            "answer": -1,
        },
        "2": {
            "milestone_id": 2,
            "answer": -1,
        },
    }


def test_update_milestone_answer_no_current_answer_session(
    user_client: TestClient,
):
    current_answer_session = user_client.get("/users/milestone-answers/2").json()
    assert current_answer_session["child_id"] == 2
    # a new answer session is created with id 100 (id 99 is the last one in the db)
    assert current_answer_session["id"] == 100
    # child 2 is 20 months old, so relevant milestones are
    # 3 (18 +/- 8)
    # 4 (24 +/- 10)
    # 5 (30 +/- 12)
    # all initially unanswered
    assert sorted(current_answer_session["answers"].keys()) == ["3", "4", "5"]
    assert current_answer_session["answers"]["3"]["answer"] == -1
    assert current_answer_session["answers"]["4"]["answer"] == -1
    assert current_answer_session["answers"]["5"]["answer"] == -1

    # answer milestone 4
    new_answer_4 = {
        "milestone_id": 4,
        "answer": 2,
    }
    response = user_client.put(
        f"/users/milestone-answers/{current_answer_session['id']}", json=new_answer_4
    )
    assert response.status_code == 200
    assert response.json()["answer"] == new_answer_4
    assert response.json()["session_completed"] is False
    # check that the answer session is still the same one
    new_answer_session = user_client.get("/users/milestone-answers/2").json()
    assert new_answer_session["id"] == 100
    assert new_answer_session["answers"]["4"] == new_answer_4

    # answer milestone 5
    new_answer_5 = {
        "milestone_id": 5,
        "answer": 3,
    }
    response = user_client.put(
        f"/users/milestone-answers/{current_answer_session['id']}", json=new_answer_5
    )
    assert response.status_code == 200
    assert response.json()["answer"] == new_answer_5
    assert response.json()["session_completed"] is False
    # check that the answer session is still the same one
    new_answer_session = user_client.get("/users/milestone-answers/2").json()
    assert new_answer_session["id"] == 100
    assert new_answer_session["answers"]["5"] == new_answer_5

    # answer the final milestone in the session
    new_answer_3 = {
        "milestone_id": 3,
        "answer": 1,
    }
    response = user_client.put(
        f"/users/milestone-answers/{current_answer_session['id']}", json=new_answer_3
    )
    assert response.status_code == 200
    assert response.json()["answer"] == new_answer_3
    assert response.json()["session_completed"] is True
    # check that we get a new answer session
    new_answer_session = user_client.get("/users/milestone-answers/2").json()
    assert new_answer_session["id"] == 101
    # answers are initially set to -1
    assert new_answer_session["answers"]["3"]["answer"] == -1
    assert new_answer_session["answers"]["4"]["answer"] == -1
    # except if that milestone was previously answered with a 3, in which case it is set to 3:
    assert new_answer_session["answers"]["5"]["answer"] == 3


def test_update_milestone_answer_update_existing_answer(user_client: TestClient):
    current_answer_session = user_client.get("/users/milestone-answers/1").json()
    assert current_answer_session["answers"]["1"] == {
        "milestone_id": 1,
        "answer": -1,
    }
    new_answer = {
        "milestone_id": 1,
        "answer": 2,
    }
    response = user_client.put(
        f"/users/milestone-answers/{current_answer_session['id']}", json=new_answer
    )
    assert response.status_code == 200
    assert response.json()["answer"] == new_answer
    assert response.json()["session_completed"] is False
    assert (
        user_client.get("/users/milestone-answers/1").json()["answers"]["1"]
        == new_answer
    )


def test_update_milestone_answer_invalid_user(research_client: TestClient):
    response = research_client.put(
        "/users/milestone-answers/1", json={"milestone_id": 1, "answer": 2}
    )
    assert response.status_code == 401


def test_update_milestone_answer_invalid_answer_session(user_client: TestClient):
    response = user_client.put(
        "/users/milestone-answers/16", json={"milestone_id": 1, "answer": 2}
    )
    assert response.status_code == 404


def test_get_current_user_answers_works(user_client: TestClient):
    response = user_client.get("/users/user-answers/")
    assert response.status_code == 200
    assert response.json() == [
        {"answer": "lorem ipsum", "additional_answer": None, "question_id": 1},
        {"answer": "other", "additional_answer": "dolor sit", "question_id": 2},
    ]


def test_get_current_user_answers_invalid_user(public_client: TestClient):
    response = public_client.get("/users/user_answers/")
    assert response.status_code == 401


def test_update_current_user_answers_prexisting(user_client: TestClient):
    publicanswers = [
        {
            "answer": "other",
            "question_id": 1,
            "additional_answer": "dolor",
        },
        {
            "answer": "amet",
            "question_id": 2,
            "additional_answer": None,
        },
    ]

    response = user_client.put(
        "/users/user-answers/",
        json=publicanswers,
    )
    assert response.status_code == 200
    assert response.json() == publicanswers

    response = user_client.get("/users/user-answers/")
    assert response.status_code == 200
    assert response.json() == publicanswers


def test_update_current_user_answers_no_prexisting(user_client2: TestClient):
    publicanswers = [
        {
            "answer": "other",
            "question_id": 1,
            "additional_answer": "dolor",
        },
        {
            "answer": "amet",
            "question_id": 2,
            "additional_answer": None,
        },
    ]

    response = user_client2.put(
        "/users/user-answers/",
        json=publicanswers,
    )

    assert response.status_code == 200
    assert response.json() == publicanswers

    response = user_client2.get("/users/user-answers/")
    assert response.status_code == 200
    assert response.json() == publicanswers


def test_get_current_child_answers_works(user_client: TestClient):
    response = user_client.get("/users/children-answers/1")
    assert response.status_code == 200
    assert response.json() == {
        "1": {
            "answer": "a",
            "question_id": 1,
            "additional_answer": None,
        },
        "2": {
            "answer": "other",
            "question_id": 2,
            "additional_answer": "apple",
        },
    }


def test_get_current_child_answers_invalid_child(user_client: TestClient):
    response = user_client.get("/users/children-answers/5")
    assert response.status_code == 404


def test_get_current_child_answers_invalid_user(public_client: TestClient):
    response = public_client.get("/users/children-answers/1")
    assert response.status_code == 401


def test_update_current_child_answers_prexisting(
    user_client: TestClient, child_answers: dict[str, str | int | None]
):
    response = user_client.put(
        "/users/children-answers/1",
        json=child_answers,
    )

    assert response.status_code == 200

    assert response.json() == {"ok": True}

    response = user_client.get(
        "/users/children-answers/1",
    )
    assert response.json() == child_answers


def test_update_current_child_answers_no_prexisting(
    user_client2: TestClient, child_answers: dict[str, str | int | None]
):
    response = user_client2.put(
        "/users/children-answers/2",
        json=child_answers,
    )
    assert response.status_code == 404


def test_get_summary_feedback_for_session(user_client: TestClient, session):
    response = user_client.get("/users/feedback/answersession=1/summary")
    assert response.status_code == 200
    # not enough samples to provide milestone group feedback
    assert response.json() == {"1": -2}


def test_get_summary_feedback_for_session_invalid(user_client: TestClient):
    response = user_client.get("/users/feedback/answersession=12/summary")
    assert response.status_code == 404


def test_get_detailed_feedback_for_session(user_client: TestClient, session):
    response = user_client.get("/users/feedback/answersession=1/detailed")
    assert response.status_code == 200
    assert response.json() == {"1": {"1": 0, "2": 1}}


def test_get_detailed_feedback_for_session_invalid(user_client: TestClient):
    response = user_client.get("/users/feedback/answersession=12/detailed")
    assert response.status_code == 404


def test_get_milestone_answer_sessions_for_statistics(user_client: TestClient, session):
    response = user_client.get("/users/milestone-answers-sessions/2")
    assert response.status_code == 200
    # child 2 has no answer sessions
    assert response.json() == {}

    response = user_client.get("/users/milestone-answers-sessions/1")
    assert response.status_code == 200
    # child 1 has 3 completed answer sessions with ids 1, 2 & 4
    assert sorted(response.json().keys()) == ["1", "2", "4"]
