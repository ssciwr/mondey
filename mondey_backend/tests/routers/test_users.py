import datetime
import pathlib

from fastapi.testclient import TestClient
from sqlmodel import select

from mondey_backend.models.milestones import MilestoneAnswer


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


def test_get_children(
    user_client: TestClient, children: list[dict[str, str | bool | int]]
):
    response = user_client.get("/users/children/")
    assert response.status_code == 200
    assert response.json() == [children[0], children[1]]


def test_get_children_no_children(research_client: TestClient):
    response = research_client.get("/users/children/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_children_admin_user_1_child(
    admin_client: TestClient, children: list[dict[str, str | bool | int]]
):
    response = admin_client.get("/users/children/")
    assert response.status_code == 200
    assert response.json() == [children[2]]


def test_get_children_invalid_user(public_client: TestClient):
    response = public_client.get("/users/children/")
    assert response.status_code == 401


def test_get_child_image(user_client: TestClient):
    response = user_client.get("/users/children-images/2")
    assert response.status_code == 200


def test_get_child_image_no_image(user_client: TestClient):
    response = user_client.get("/users/children-images/11")
    assert response.status_code == 404


def test_create_update_and_delete_child(user_client: TestClient):
    assert len(user_client.get("/users/children/").json()) == 2
    response_create = user_client.post(
        "/users/children/",
        json={
            "name": "child1",
            "birth_year": 2021,
            "birth_month": 3,
        },
    )
    assert response_create.status_code == 200
    assert response_create.json() == {
        "id": 4,
        "name": "child1",
        "birth_year": 2021,
        "birth_month": 3,
        "has_image": False,
    }
    assert len(user_client.get("/users/children/").json()) == 3
    response_update = user_client.put(
        "/users/children/",
        json={
            "id": 4,
            "name": "c",
            "birth_year": 2020,
            "birth_month": 9,
            "has_image": False,
        },
    )
    assert response_update.status_code == 200
    assert response_update.json() == {
        "id": 4,
        "name": "c",
        "birth_year": 2020,
        "birth_month": 9,
        "has_image": False,
    }
    assert len(user_client.get("/users/children/").json()) == 3
    response_delete = user_client.delete("/users/children/4")
    assert response_delete.status_code == 200
    assert len(user_client.get("/users/children/").json()) == 2


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


def test_get_milestone_answers_child3_no_current_answer_session(
    admin_client: TestClient,
):
    response = admin_client.get("/users/milestone-answers/3")
    assert response.status_code == 200
    assert response.json()["id"] == 4
    assert response.json()["child_id"] == 3
    assert _is_approx_now(response.json()["created_at"])
    assert response.json()["answers"] == {}


def test_get_milestone_answers_child1_current_answer_session(user_client: TestClient):
    response = user_client.get("/users/milestone-answers/1")
    assert response.status_code == 200
    assert response.json()["id"] == 2
    assert response.json()["child_id"] == 1
    assert response.json()["answers"] == {
        "1": {
            "milestone_id": 1,
            "answer": 3,
        },
        "2": {
            "milestone_id": 2,
            "answer": 2,
        },
    }
    assert _is_approx_now(response.json()["created_at"])


def test_update_milestone_answer_no_current_answer_session(
    user_client: TestClient,
):
    current_answer_session = user_client.get("/users/milestone-answers/2").json()
    assert current_answer_session["child_id"] == 2

    # child 2 is 20 months old, so milestones 4
    assert current_answer_session["answers"]["4"]["answer"] == -1
    new_answer = {
        "milestone_id": 4,
        "answer": 2,
    }
    response = user_client.put(
        f"/users/milestone-answers/{current_answer_session['id']}", json=new_answer
    )
    assert response.status_code == 200
    assert response.json() == new_answer
    new_answer_session = user_client.get("/users/milestone-answers/2").json()
    assert new_answer_session["answers"]["4"] == new_answer


def test_update_milestone_answer_update_existing_answer(user_client: TestClient):
    current_answer_session = user_client.get("/users/milestone-answers/1").json()
    assert current_answer_session["answers"]["1"] == {
        "milestone_id": 1,
        "answer": 3,
    }
    new_answer = {
        "milestone_id": 1,
        "answer": 2,
    }
    response = user_client.put(
        f"/users/milestone-answers/{current_answer_session['id']}", json=new_answer
    )
    assert response.status_code == 200
    assert response.json() == new_answer
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
            "additional_answer": "dolor sit",
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
    answers = session.exec(
        select(MilestoneAnswer).where(MilestoneAnswer.answer_session_id == 1)
    ).all()
    for answer in answers:
        answer.included_in_milestone_statistics = False
        answer.included_in_milestonegroup_statistics = False
        session.merge(answer)
    session.commit()

    response = user_client.get("/users/feedback/answersession=1/summary")
    assert response.status_code == 200
    assert response.json() == {"1": 2}


def test_get_summary_feedback_for_session_invalid(user_client: TestClient):
    response = user_client.get("/users/feedback/answersession=12/summary")
    assert response.status_code == 404


def test_get_detailed_feedback_for_session(user_client: TestClient, session):
    answers = session.exec(
        select(MilestoneAnswer).where(MilestoneAnswer.answer_session_id == 1)
    ).all()
    for answer in answers:
        answer.included_in_milestone_statistics = False
        answer.included_in_milestonegroup_statistics = False
        session.merge(answer)
    session.commit()
    response = user_client.get("/users/feedback/answersession=1/detailed")
    assert response.status_code == 200
    assert response.json() == {"1": {"1": 2, "2": 2}}


def test_get_detailed_feedback_for_session_invalid(user_client: TestClient):
    response = user_client.get("/users/feedback/answersession=12/detailed")
    assert response.status_code == 404
