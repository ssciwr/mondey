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
