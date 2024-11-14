import pytest
from fastapi.testclient import TestClient


def test_get_child_questions(user_client: TestClient):
    response = user_client.get("/child-questions/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user_questions(user_client: TestClient):
    response = user_client.get("/user-questions/")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.parametrize("entity", ["child-questions", "user-questions"])
@pytest.mark.parametrize(
    ("order_items", "ids_in_order"),
    [([(1, 1), (2, 2)], [1, 2]), ([(1, 2), (2, 1)], [2, 1])],
)
def test_order_items(
    admin_client: TestClient,
    entity: str,
    order_items: list[tuple[int, int]],
    ids_in_order: list[int],
):
    order = [{"id": item_id, "order": order} for item_id, order in order_items]
    response = admin_client.post(f"/admin/{entity}/order/", json=order)
    assert response.status_code == 200
    items = admin_client.get(f"/{entity}/").json()
    for idx, item_id in enumerate(ids_in_order):
        assert items[idx]["id"] == item_id
