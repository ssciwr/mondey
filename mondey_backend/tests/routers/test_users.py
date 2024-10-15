import pathlib

from fastapi.testclient import TestClient


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
