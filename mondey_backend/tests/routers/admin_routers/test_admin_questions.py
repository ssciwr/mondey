from fastapi.testclient import TestClient
from sqlmodel import select

from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion


def test_get_user_question_admin_works(admin_client: TestClient, user_questions):
    response = admin_client.get("/admin/user-questions/")

    assert response.status_code == 200

    assert [element["order"] for element in response.json()] == [1, 2]
    assert response.json() == user_questions


def test_create_user_question_works(admin_client: TestClient):
    response = admin_client.post("/admin/user-questions/")
    assert response.status_code == 200
    assert response.json() == {
        "id": 3,
        "name": "",
        "order": 0,
        "component": "select",
        "type": "text",
        "options": "",
        "text": {
            "de": {
                "options_json": "",
                "user_question_id": 3,
                "options": "",
                "lang_id": "de",
                "question": "",
            },
            "en": {
                "options_json": "",
                "user_question_id": 3,
                "options": "",
                "lang_id": "en",
                "question": "",
            },
            "fr": {
                "options_json": "",
                "user_question_id": 3,
                "options": "",
                "lang_id": "fr",
                "question": "",
            },
        },
        "additional_option": "",
        "required": False,
    }


def test_update_user_question_works(
    admin_client: TestClient, default_user_question_admin
):
    response = admin_client.put(
        "/admin/user-questions/", json=default_user_question_admin
    )

    assert response.status_code == 200

    assert response.json() == default_user_question_admin


def test_update_user_question_id_not_there(admin_client: TestClient):
    user_question_admin = {
        "id": 5,
        "name": "User Question 5",
        "component": "textarea",
        "type": "other_thing",
        "order": 0,
        "options": "some_options",
        "text": {
            "de": {
                "options_json": "",
                "user_question_id": 5,
                "options": "",
                "lang_id": "de",
                "question": "",
            },
            "en": {
                "options_json": "",
                "user_question_id": 5,
                "options": "",
                "lang_id": "en",
                "question": "",
            },
            "fr": {
                "options_json": "",
                "user_question_id": 5,
                "options": "",
                "lang_id": "fr",
                "question": "",
            },
        },
        "additional_option": "nothing",
    }

    response = admin_client.put("/admin/user-questions/", json=user_question_admin)

    assert response.status_code == 404


def test_delete_user_question_deletes(session, admin_client: TestClient):
    response = admin_client.delete("/admin/user-questions/1?dry_run=false")

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["ok"]
    assert response_json["deletion_executed"]

    user_questions = session.exec(select(UserQuestion)).all()
    assert len(user_questions) == 1
    assert user_questions[0].id == 2


def test_delete_user_question_works(session, admin_client: TestClient):
    user_questions = session.exec(select(UserQuestion)).all()
    assert len(user_questions) == 2

    user_answers = session.exec(select(UserAnswer)).all()
    assert len(user_answers) == 2

    response = admin_client.delete("/admin/user-questions/1")  # dry run
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["ok"]
    assert response_json["would_delete"]
    assert response_json["would_delete"]["total_answers"] == 1

    user_questions = session.exec(select(UserQuestion)).all()
    assert len(user_questions) == 2

    response = admin_client.delete(
        "/admin/user-questions/1?dry_run=false"
    )  # really delete
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["ok"]
    assert response_json["deletion_executed"]

    user_questions = session.exec(select(UserQuestion)).all()
    assert len(user_questions) == 1
    assert user_questions[0].id == 2

    user_answers = session.exec(select(UserAnswer)).all()
    assert len(user_answers) == 1
    for user_answer in user_answers:
        assert user_answer.question_id != 1  # because they don't have answer IDs.


def test_delete_user_question_id_not_there(admin_client: TestClient):
    response = admin_client.delete("/admin/user-questions/12")

    assert response.status_code == 404


def test_get_child_question_admin_works(admin_client: TestClient, child_questions):
    response = admin_client.get("/admin/child-questions/")

    assert response.status_code == 200
    assert [element["order"] for element in response.json()] == [0, 1]
    assert response.json() == child_questions


def test_create_child_question_works(admin_client: TestClient):
    response = admin_client.post("/admin/child-questions/")

    assert response.status_code == 200
    assert response.json() == {
        "id": 3,
        "name": "",
        "order": 0,
        "component": "select",
        "type": "text",
        "options": "",
        "text": {
            "de": {
                "options_json": "",
                "child_question_id": 3,
                "options": "",
                "lang_id": "de",
                "question": "",
            },
            "en": {
                "options_json": "",
                "child_question_id": 3,
                "options": "",
                "lang_id": "en",
                "question": "",
            },
            "fr": {
                "options_json": "",
                "child_question_id": 3,
                "options": "",
                "lang_id": "fr",
                "question": "",
            },
        },
        "additional_option": "",
        "required": False,
    }


def test_update_child_question_works(admin_client: TestClient):
    child_question_admin = {
        "id": 2,
        "name": "Child Question 2",
        "component": "textarea",
        "type": "other_thing",
        "order": 0,
        "options": "some_options",
        "text": {
            "de": {
                "options_json": "",
                "child_question_id": 2,
                "options": "",
                "lang_id": "de",
                "question": "",
            },
            "en": {
                "options_json": "",
                "child_question_id": 2,
                "options": "",
                "lang_id": "en",
                "question": "",
            },
            "fr": {
                "options_json": "",
                "child_question_id": 2,
                "options": "",
                "lang_id": "fr",
                "question": "",
            },
        },
        "additional_option": "nothing",
    }
    response = admin_client.put("/admin/child-questions", json=child_question_admin)
    assert response.status_code == 200


def test_update_child_question_id_not_there(admin_client: TestClient):
    child_question_admin = {
        "id": 5,
        "name": "Child Question 5",
        "component": "textarea",
        "type": "other_thing",
        "order": 0,
        "options": "some_options",
        "text": {
            "de": {
                "options_json": "",
                "child_question_id": 5,
                "options": "",
                "lang_id": "de",
                "question": "",
            },
            "en": {
                "options_json": "",
                "child_question_id": 5,
                "options": "",
                "lang_id": "en",
                "question": "",
            },
            "fr": {
                "options_json": "",
                "child_question_id": 5,
                "options": "",
                "lang_id": "fr",
                "question": "",
            },
        },
        "additional_option": "nothing",
    }
    response = admin_client.put("/admin/child-questions/", json=child_question_admin)
    assert response.status_code == 404


def test_delete_child_question_works(session, admin_client: TestClient):
    child_questions = session.exec(select(ChildQuestion)).all()
    assert len(child_questions) == 2

    child_answers = session.exec(select(ChildAnswer)).all()
    assert len(child_answers) == 2

    response = admin_client.delete("/admin/child-questions/1")  # dry run
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["ok"]
    assert response_json["would_delete"]
    assert response_json["would_delete"]["total_answers"] == 1

    child_questions = session.exec(select(ChildQuestion)).all()
    assert len(child_questions) == 2

    response = admin_client.delete(
        "/admin/child-questions/1?dry_run=false"
    )  # really delete
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["ok"]
    assert response_json["deletion_executed"]

    child_questions = session.exec(select(ChildQuestion)).all()
    assert len(child_questions) == 1
    assert child_questions[0].id == 2

    child_answers = session.exec(select(ChildAnswer)).all()
    assert len(child_answers) == 1
    for child_answer in child_answers:
        assert child_answer.question_id != 1  # because they don't have answer IDs.


def test_delete_child_question_id_not_there(admin_client: TestClient):
    response = admin_client.delete("/admin/child-questions/12")
    assert response.status_code == 404
