import json
import pathlib

import pytest
from fastapi.testclient import TestClient


def test_post_language(admin_client: TestClient):
    response = admin_client.post("/admin/languages/", json={"id": "es"})
    assert response.status_code == 200
    assert response.json() == {"id": "es"}


def test_post_language_invalid_already_exists(admin_client: TestClient):
    response = admin_client.post("/admin/languages/", json={"id": "de"})
    assert response.status_code == 400


def test_delete_language(admin_client: TestClient):
    response = admin_client.delete("/admin/languages/fr")
    assert response.status_code == 200
    assert admin_client.get("/languages").json() == ["de", "en"]


@pytest.mark.parametrize("lang_id", ["de", "en"])
def test_delete_language_invalid_de_en_cannot_be_deleted(
    admin_client: TestClient, lang_id: str
):
    response = admin_client.delete(f"/admin/languages/{lang_id}")
    assert response.status_code == 400


def test_delete_language_invalid_language_id(admin_client: TestClient):
    response = admin_client.delete("/admin/languages/zz")
    assert response.status_code == 404


def test_update_i18n(admin_client: TestClient, static_dir: pathlib.Path):
    assert admin_client.post("/admin/languages/", json={"id": "nl"}).status_code == 200
    i18_json_path = static_dir / "i18n" / "nl.json"
    i18_json = {
        "s1": {"k1": "v1", "k2": "v2"},
        "accents": {"k1": "v1", "äéœ": "óíüúëþ"},
    }
    assert not i18_json_path.is_file()
    response = admin_client.put("/admin/i18n/nl", json=i18_json)
    assert response.status_code == 200
    assert i18_json_path.is_file()
    with open(i18_json_path) as f:
        assert json.load(f) == i18_json
    i18_json["s1"]["k1"] = "MODIFIED!"
    response = admin_client.put("/admin/i18n/nl", json=i18_json)
    assert response.status_code == 200
    with open(i18_json_path) as f:
        assert json.load(f) == i18_json


def test_update_i18n_invalid_json(admin_client: TestClient, static_dir: pathlib.Path):
    i18_json = {
        "valid-section": {"key1": "value1"},
        "invalid-section": "this-value-should-be-a-dict!",
    }
    response = admin_client.put("/admin/i18n/en", json=i18_json)
    assert response.status_code == 422


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


def test_delete_milestone_group(admin_client: TestClient):
    assert admin_client.get("/milestone-groups/2").status_code == 200
    response = admin_client.delete("/admin/milestone-groups/2")
    assert response.status_code == 200
    assert admin_client.get("/milestone-groups/2").status_code == 404
    response = admin_client.delete("/admin/milestone-groups/2")
    assert response.status_code == 404


def test_delete_milestone_group_invalid_group_id(admin_client: TestClient):
    response = admin_client.delete("/admin/milestone-groups/692")
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


def test_put_milestone_group_image(
    admin_client: TestClient, static_dir: pathlib.Path, jpg_file: pathlib.Path
):
    static_dir_jpg = static_dir / "mg1.jpg"
    assert not static_dir_jpg.is_file()
    with open(jpg_file, "rb") as f:
        response = admin_client.put(
            "/admin/milestone-group-images/1",
            files={"file": ("filename", f, "image/jpeg")},
        )
    assert response.status_code == 200
    assert static_dir_jpg.is_file()


def test_post_milestone(admin_client: TestClient):
    response = admin_client.post("/admin/milestones/2")
    assert response.status_code == 200
    assert response.json() == {
        "id": 6,
        "group_id": 2,
        "order": 0,
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
    milestone["order"] = 6
    milestone["text"]["de"]["title"] = "asdsd"
    milestone["text"]["de"]["desc"] = "12xzascdasdf"
    milestone["text"]["de"]["obs"] = "asdrgf"
    milestone["text"]["de"]["help"] = "jgfhj"
    milestone["text"]["en"]["title"] = "asqwdreqweqw"
    milestone["text"]["en"]["desc"] = "th567"
    response = admin_client.put("/admin/milestones", json=milestone)
    assert response.status_code == 200
    assert response.json() == milestone


def test_delete_milestone(admin_client: TestClient):
    assert admin_client.get("/milestones/2").status_code == 200
    response = admin_client.delete("/admin/milestones/2")
    assert response.status_code == 200
    assert admin_client.get("/milestones/2").status_code == 404
    response = admin_client.delete("/admin/milestones/2")
    assert response.status_code == 404


def test_post_milestone_image(
    admin_client: TestClient, static_dir: pathlib.Path, jpg_file: pathlib.Path
):
    # 3 milestone images already exist
    assert len(admin_client.get("/milestones/1").json()["images"]) == 2
    assert len(admin_client.get("/milestones/2").json()["images"]) == 1
    assert len(admin_client.get("/milestones/3").json()["images"]) == 0
    assert len(admin_client.get("/milestones/4").json()["images"]) == 0
    assert len(admin_client.get("/milestones/5").json()["images"]) == 0
    # image ids are sequential
    image_id = 3
    # add an image to each milestone
    for milestone_id in [1, 2, 3, 4, 5]:
        image_id += 1
        filename = f"m{image_id}.jpg"
        static_dir_jpg = static_dir / filename
        assert not static_dir_jpg.is_file()
        with open(jpg_file, "rb") as f:
            response = admin_client.post(
                f"/admin/milestone-images/{milestone_id}",
                files={"file": ("filename", f, "image/jpeg")},
            )
        assert response.status_code == 200
        assert response.json()["filename"] == filename
        assert static_dir_jpg.is_file()
    assert len(admin_client.get("/milestones/1").json()["images"]) == 3
    assert len(admin_client.get("/milestones/2").json()["images"]) == 2
    assert len(admin_client.get("/milestones/3").json()["images"]) == 1
    assert len(admin_client.get("/milestones/4").json()["images"]) == 1
    assert len(admin_client.get("/milestones/5").json()["images"]) == 1


# tests for user questions


def test_get_user_question_admin_works(admin_client: TestClient):
    response = admin_client.get("/admin/user-questions")

    assert response.status_code == 200

    assert [element["order"] for element in response.json()] == [1, 2]
    print("response: ", response.json())
    assert response.json() == [
        {
            "id": 1,
            "order": 1,
            "component": "select",
            "options": "[a,b,c,other]",
            "additional_option": "other",
            "type": "text",
            "text": {
                "de": {
                    "question_id": 1,
                    "lang_id": "de",
                    "options": "[x,y,z]",
                    "options_json": "",
                    "question": "Wo sonst?",
                },
                "en": {
                    "question_id": 1,
                    "lang_id": "en",
                    "options": "[1,2,3]",
                    "question": "Where else?",
                    "options_json": "",
                },
            },
        },
        {
            "id": 2,
            "order": 2,
            "component": "textarea",
            "options": "[a2,b2,c2,other]",
            "additional_option": "other",
            "type": "text",
            "text": {
                "de": {
                    "question_id": 2,
                    "lang_id": "de",
                    "options": "[x2,y2,z2]",
                    "options_json": "",
                    "question": "Was noch?",
                },
                "en": {
                    "question_id": 2,
                    "lang_id": "en",
                    "options": "[12,22,32]",
                    "question": "What else?",
                    "options_json": "",
                },
            },
        },
    ]


def test_create_user_question_works():
    assert 3 == 5


def test_create_user_question_id_exists():
    assert 3 == 5


def test_create_user_question_id_database_error():
    assert 3 == 5


def test_update_user_question_works():
    assert 3 == 5


def test_update_user_question_id_not_there():
    assert 3 == 5


def test_update_user_question_database_error():
    assert 3 == 5


def test_delete_user_question_works():
    assert 3 == 5


def test_delete_user_question_id_not_there():
    assert 3 == 5


def test_delete_user_question_database_error():
    assert 3 == 5


def test_get_child_question_admin_works(admin_client: TestClient):
    response = admin_client.get("/admin/child-questions")

    assert response.status_code == 200

    assert [element["order"] for element in response.json()] == [0, 1]
    assert response.json() == [
        {
            "id": 1,
            "order": 0,
            "component": "select",
            "options": "[a,b,c,other]",
            "additional_option": "other",
            "type": "text",
            "text": {
                "de": {
                    "question_id": 1,
                    "lang_id": "de",
                    "options": "[x,y,z]",
                    "options_json": "",
                    "question": "was?",
                },
                "en": {
                    "question_id": 1,
                    "lang_id": "en",
                    "options": "[1,2,3]",
                    "question": "what?",
                    "options_json": "",
                },
            },
        },
        {
            "id": 2,
            "order": 1,
            "component": "select",
            "options": "[a2,b2,c2,other]",
            "additional_option": "other",
            "type": "text",
            "text": {
                "de": {
                    "question_id": 2,
                    "lang_id": "de",
                    "options": "[x2,y2,z2]",
                    "options_json": "",
                    "question": "Wo?",
                },
                "en": {
                    "question_id": 2,
                    "lang_id": "en",
                    "options": "[12,22,32]",
                    "question": "Where?",
                    "options_json": "",
                },
            },
        },
    ]


def test_create_child_question_works():
    assert 3 == 5


def test_create_child_question_id_exists():
    assert 3 == 5


def test_create_child_question_id_database_error():
    assert 3 == 5


def test_update_child_question_works():
    assert 3 == 5


def test_update_child_question_id_not_there():
    assert 3 == 5


def test_update_child_question_database_error():
    assert 3 == 5


def test_delete_child_question_works():
    assert 3 == 5


def test_delete_child_question_id_not_there():
    assert 3 == 5


def test_delete_child_question_database_error():
    assert 3 == 5
