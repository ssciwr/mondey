import pathlib

import pytest
from fastapi.testclient import TestClient
from PIL import Image


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
    response = admin_client.delete("/admin/milestone-groups/2")
    assert response.status_code == 200
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
        "group_id": 2,
        "order": 0,
        "expected_age_months": 12,
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
    milestone["expected_age_months"] = 11
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


def test_get_milestone_age_scores(admin_client_stat: TestClient):
    response = admin_client_stat.get("/admin/milestone-age-scores/1")
    assert response.status_code == 200

    assert response.json()["expected_age"] == 8

    assert response.json()["scores"][7]["avg_score"] == pytest.approx(0.0)
    assert response.json()["scores"][7]["stddev_score"] == pytest.approx(0.0)
    assert response.json()["scores"][7]["count"] == 0

    assert response.json()["scores"][8]["avg_score"] == pytest.approx(2.0)
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
