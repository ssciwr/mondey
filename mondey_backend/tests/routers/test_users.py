import datetime
import pathlib

from fastapi.testclient import TestClient


def _is_approx_now(iso_date_string: str, delta=datetime.timedelta(hours=1)) -> bool:
    return (
        datetime.datetime.now() - datetime.datetime.fromisoformat(iso_date_string)
        < delta
    )


def test_get_children(user_client: TestClient):
    response = user_client.get("/users/children/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "birth_month": 3,
            "birth_year": 2022,
            "id": 1,
            "name": "child1",
            "has_image": False,
        },
        {
            "birth_month": 12,
            "birth_year": 2024,
            "id": 2,
            "name": "child2",
            "has_image": True,
        },
    ]


def test_get_children_no_children(research_client: TestClient):
    response = research_client.get("/users/children/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_children_admin_user_1_child(admin_client: TestClient):
    response = admin_client.get("/users/children/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "birth_month": 1,
            "birth_year": 2021,
            "id": 3,
            "name": "child3",
            "has_image": True,
        }
    ]


def test_get_children_invalid_user(public_client: TestClient):
    response = public_client.get("/users/children/")
    assert response.status_code == 401


def test_get_child_image(user_client: TestClient):
    response = user_client.get("/users/children-images/2")
    assert response.status_code == 200
    assert response.content == b"2.jpg"


def test_get_child_image_no_image(user_client: TestClient):
    response = user_client.get("/users/children-images/1")
    assert response.status_code == 404


def test_create_update_and_delete_child(user_client: TestClient):
    assert len(user_client.get("/users/children/").json()) == 2
    response_create = user_client.post(
        "/users/children/",
        json={"name": "child1", "birth_year": 2021, "birth_month": 3},
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
    user_client: TestClient, private_dir: pathlib.Path, jpg_file: pathlib.Path
):
    children_dir = private_dir / "children"
    # child 1 does not have an image:
    assert not (children_dir / "1.jpg").is_file()
    assert user_client.get("/users/children/").json()[0]["has_image"] is False
    assert user_client.get("/users/children-images/1").status_code == 404
    # add an image for the first child
    with open(jpg_file, "rb") as f:
        response = user_client.put(
            "/users/children-images/1",
            files={"file": ("filename", f, "image/jpeg")},
        )
    assert response.status_code == 200
    assert (children_dir / "1.jpg").is_file()
    assert user_client.get("/users/children/").json()[0]["has_image"] is True
    assert user_client.get("/users/children-images/1").status_code == 200
    (children_dir / "1.jpg").unlink()


def test_get_milestone_answers_user_does_not_own_child(admin_client: TestClient):
    response = admin_client.get("/users/milestone-answers/1")
    assert response.status_code == 401


def test_get_milestone_answers_child_does_not_exist(admin_client: TestClient):
    response = admin_client.get("/users/milestone-answers/8")
    assert response.status_code == 401


def test_get_milestone_answers_no_current_answer_session(admin_client: TestClient):
    response = admin_client.get("/users/milestone-answers/3")
    assert response.status_code == 200
    assert response.json()["id"] == 4
    assert _is_approx_now(response.json()["created_at"])
    assert response.json()["answers"] == {}


def test_get_milestone_answers_current_answer_session(user_client: TestClient):
    response = user_client.get("/users/milestone-answers/1")
    assert response.status_code == 200
    assert response.json()["id"] == 2
    assert response.json()["answers"] == {
        "1": {"milestone_id": 1, "answer": 0},
        "2": {"milestone_id": 2, "answer": 3},
    }
    assert _is_approx_now(response.json()["created_at"])


def test_update_milestone_answer_current_answer_session_no_existing_answer(
    user_client: TestClient,
):
    current_answer_session = user_client.get("/users/milestone-answers/1").json()
    assert "6" not in current_answer_session["answers"]
    new_answer = {"milestone_id": 6, "answer": 2}
    response = user_client.put(
        f"/users/milestone-answers/{current_answer_session['id']}", json=new_answer
    )
    assert response.status_code == 200
    assert response.json() == new_answer
    assert (
        user_client.get("/users/milestone-answers/1").json()["answers"]["6"]
        == new_answer
    )


def test_update_milestone_answer_update_existing_answer(user_client: TestClient):
    current_answer_session = user_client.get("/users/milestone-answers/1").json()
    assert current_answer_session["answers"]["1"] == {"milestone_id": 1, "answer": 0}
    new_answer = {"milestone_id": 1, "answer": 2}
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
    assert response.status_code == 401
