import pathlib

import pytest
from fastapi.testclient import TestClient


def test_post_language(admin_client: TestClient):
    response = admin_client.post("/admin/languages/", json={"lang": "es"})
    assert response.status_code == 200
    assert response.json() == {"id": 4, "lang": "es"}


def test_delete_language(admin_client: TestClient):
    response = admin_client.delete("/admin/languages/2")
    assert response.status_code == 200
    assert admin_client.get("/languages").json() == {"1": "de", "3": "fr"}


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
            "1": {
                "group_id": 3,
                "lang_id": 1,
                "title": "",
                "desc": "",
            },
            "2": {
                "group_id": 3,
                "lang_id": 2,
                "title": "",
                "desc": "",
            },
            "3": {
                "group_id": 3,
                "lang_id": 3,
                "title": "",
                "desc": "",
            },
        },
        "milestones": [],
    }


def test_put_milestone_group(admin_client: TestClient, milestone_group_admin1: dict):
    milestone_group = milestone_group_admin1
    milestone_group["order"] = 6
    milestone_group["text"]["1"]["title"] = "asdsd"
    milestone_group["text"]["1"]["desc"] = "12xzascdasdf"
    milestone_group["text"]["2"]["title"] = "asqwdreqweqw"
    milestone_group["text"]["2"]["desc"] = "th567"
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
    ["/admin/languages/1", "/admin/milestone-groups/1", "/admin/milestones/1"],
)
@pytest.mark.parametrize("client_type", ["user_client", "research_client"])
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
            "1": {
                "milestone_id": 6,
                "lang_id": 1,
                "title": "",
                "desc": "",
                "obs": "",
                "help": "",
            },
            "2": {
                "milestone_id": 6,
                "lang_id": 2,
                "title": "",
                "desc": "",
                "obs": "",
                "help": "",
            },
            "3": {
                "milestone_id": 6,
                "lang_id": 3,
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
    milestone["text"]["1"]["title"] = "asdsd"
    milestone["text"]["1"]["desc"] = "12xzascdasdf"
    milestone["text"]["1"]["obs"] = "asdrgf"
    milestone["text"]["1"]["help"] = "jgfhj"
    milestone["text"]["2"]["title"] = "asqwdreqweqw"
    milestone["text"]["2"]["desc"] = "th567"
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
