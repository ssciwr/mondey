from fastapi.testclient import TestClient
from sqlmodel import select

from mondey_backend.models.questions import ChildAnswer
from mondey_backend.models.questions import ChildQuestion
from mondey_backend.models.questions import UserAnswer
from mondey_backend.models.questions import UserQuestion


def test_get_user_question_admin_works(
    admin_client: TestClient, user_questions_with_invisible_question
):
    response = admin_client.get("/admin/user-questions/")
    assert response.status_code == 200

    assert [element["order"] for element in response.json()] == [1, 2, 3]
    assert response.json() == user_questions_with_invisible_question


def test_visbility_hidden_questions_only_included_in_admin_endpoint(
    admin_client: TestClient, user_questions, user_questions_with_invisible_question
):
    response = admin_client.get("/admin/user-questions/")
    assert response.status_code == 200

    assert [element["order"] for element in response.json()] == [1, 2, 3]
    assert len(user_questions_with_invisible_question) == 3
    assert response.json() == user_questions_with_invisible_question

    response_as_user = admin_client.get("/user-questions/")
    assert response_as_user.status_code == 200

    assert len(response_as_user.json()) == 2
    assert len(user_questions) == 2

    # Check that Question 3 (not visible) is not included in the response
    for question in response_as_user.json():
        assert question.get("id") != 3, (
            "Question 3 should not be visible in the response"
        )


def test_create_user_question_works(admin_client: TestClient):
    response = admin_client.post("/admin/user-questions/")
    assert response.status_code == 200
    assert response.json() == {
        "id": 4,
        "name": "",
        "order": 0,
        "component": "select",
        "type": "text",
        "options": "",
        "text": {
            "de": {
                "options_json": "",
                "user_question_id": 4,
                "options": "",
                "lang_id": "de",
                "question": "",
            },
            "en": {
                "options_json": "",
                "user_question_id": 4,
                "options": "",
                "lang_id": "en",
                "question": "",
            },
            "fr": {
                "options_json": "",
                "user_question_id": 4,
                "options": "",
                "lang_id": "fr",
                "question": "",
            },
        },
        "additional_option": "",
        "required": False,
        "visibility": False,
        "depends_on_question_id": None,
        "show_if_answer": "",
    }


def test_update_user_question_works(
    admin_client: TestClient, default_user_question_admin
):
    response = admin_client.put(
        "/admin/user-questions/", json=default_user_question_admin
    )

    assert response.status_code == 200

    assert response.json() == default_user_question_admin


def test_update_user_question_dependency_fields(
    admin_client: TestClient, default_user_question_admin
):
    # make question 1 depend on the answer to question 2
    user_question_admin = {
        **default_user_question_admin,
        "visibility": True,
        "depends_on_question_id": 2,
        "show_if_answer": "a;b",
    }
    response = admin_client.put("/admin/user-questions/", json=user_question_admin)
    assert response.status_code == 200
    assert response.json()["depends_on_question_id"] == 2
    assert response.json()["show_if_answer"] == "a;b"

    # the dependency fields are also exposed via the public endpoint
    public_response = admin_client.get("/user-questions/")
    assert public_response.status_code == 200
    question_1 = next(q for q in public_response.json() if q["id"] == 1)
    assert question_1["depends_on_question_id"] == 2
    assert question_1["show_if_answer"] == "a;b"


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

    user_questions = session.exec(select(UserQuestion)).all()
    assert len(user_questions) == 2
    assert user_questions[0].id == 2


def test_delete_user_question_clears_dependent_questions(
    session, admin_client: TestClient
):
    dependent_question = session.get(UserQuestion, 2)
    assert dependent_question is not None
    dependent_question.depends_on_question_id = 1
    dependent_question.show_if_answer = "yes"
    session.add(dependent_question)
    session.commit()

    response = admin_client.delete("/admin/user-questions/1?dry_run=false")

    assert response.status_code == 200
    session.refresh(dependent_question)
    assert dependent_question.depends_on_question_id is None
    assert dependent_question.show_if_answer == ""


def test_delete_user_question_works(session, admin_client: TestClient):
    user_questions = session.exec(select(UserQuestion)).all()
    assert len(user_questions) == 3

    user_answers = session.exec(select(UserAnswer)).all()
    assert len(user_answers) == 2

    response = admin_client.delete("/admin/user-questions/1")  # dry run
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["ok"]
    assert response_json["children"]
    assert response_json["children"]["affectedQuestionAnswers"] == 1

    user_questions = session.exec(select(UserQuestion)).all()
    assert len(user_questions) == 3

    response = admin_client.delete(
        "/admin/user-questions/1?dry_run=false"
    )  # really delete
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["ok"]

    user_questions = session.exec(select(UserQuestion)).all()
    assert len(user_questions) == 2
    assert user_questions[0].id == 2

    user_answers = session.exec(select(UserAnswer)).all()
    assert len(user_answers) == 1
    for user_answer in user_answers:
        assert user_answer.question_id != 1  # because they don't have answer IDs.


def test_delete_user_question_id_not_there(admin_client: TestClient):
    response = admin_client.delete("/admin/user-questions/12")

    assert response.status_code == 404


def test_visbility_hidden_child_questions_only_included_in_admin_endpoint(
    admin_client: TestClient, child_questions, child_questions_with_invisible_question
):
    response = admin_client.get("/admin/child-questions/")
    assert response.status_code == 200

    assert [element["order"] for element in response.json()] == [0, 1, 2]
    assert len(child_questions_with_invisible_question) == 3
    assert response.json() == child_questions_with_invisible_question

    response_as_child = admin_client.get("/child-questions/")
    assert response_as_child.status_code == 200

    assert len(response_as_child.json()) == 2
    assert len(child_questions) == 2

    # Check that Question 3 (not visible) is not included in the response
    for question in response_as_child.json():
        assert question.get("id") != 3, (
            "Question 3 should not be visible in the response"
        )


def test_create_child_question_works(admin_client: TestClient):
    response = admin_client.post("/admin/child-questions/")

    assert response.status_code == 200
    assert response.json() == {
        "id": 4,
        "name": "",
        "order": 0,
        "component": "select",
        "type": "text",
        "options": "",
        "text": {
            "de": {
                "options_json": "",
                "child_question_id": 4,
                "options": "",
                "lang_id": "de",
                "question": "",
            },
            "en": {
                "options_json": "",
                "child_question_id": 4,
                "options": "",
                "lang_id": "en",
                "question": "",
            },
            "fr": {
                "options_json": "",
                "child_question_id": 4,
                "options": "",
                "lang_id": "fr",
                "question": "",
            },
        },
        "additional_option": "",
        "required": False,
        "visibility": False,
        "depends_on_question_id": None,
        "show_if_answer": "",
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
    assert len(child_questions) == 3

    child_answers = session.exec(select(ChildAnswer)).all()
    assert len(child_answers) == 2

    response = admin_client.delete("/admin/child-questions/1")  # dry run
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["ok"]
    assert response_json["children"]
    assert response_json["children"]["affectedQuestionAnswers"] == 1

    child_questions = session.exec(select(ChildQuestion)).all()
    assert len(child_questions) == 3

    response = admin_client.delete(
        "/admin/child-questions/1?dry_run=false"
    )  # really delete
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["ok"]

    child_questions = session.exec(select(ChildQuestion)).all()
    assert len(child_questions) == 2
    assert child_questions[0].id == 2

    child_answers = session.exec(select(ChildAnswer)).all()
    assert len(child_answers) == 1
    for child_answer in child_answers:
        assert child_answer.question_id != 1  # because they don't have answer IDs.


def test_delete_child_question_clears_dependent_questions(
    session, admin_client: TestClient
):
    dependent_question = session.get(ChildQuestion, 2)
    assert dependent_question is not None
    dependent_question.depends_on_question_id = 1
    dependent_question.show_if_answer = "yes"
    session.add(dependent_question)
    session.commit()

    response = admin_client.delete("/admin/child-questions/1?dry_run=false")

    assert response.status_code == 200
    session.refresh(dependent_question)
    assert dependent_question.depends_on_question_id is None
    assert dependent_question.show_if_answer == ""


def test_delete_child_question_id_not_there(admin_client: TestClient):
    response = admin_client.delete("/admin/child-questions/12")
    assert response.status_code == 404
