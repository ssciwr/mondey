import json
import pathlib

import pytest
from fastapi.testclient import TestClient


def test_post_language(admin_client: TestClient):
    # initially no spanish language texts
    for milestone_group in admin_client.get("/admin/milestone-groups/").json():
        assert "es" not in milestone_group["text"]
        for milestone in milestone_group["milestones"]:
            assert "es" not in milestone["text"]
    for user_question in admin_client.get("/admin/user-questions/").json():
        assert "es" not in user_question["text"]
    for child_question in admin_client.get("/admin/child-questions/").json():
        assert "es" not in child_question["text"]
    # add spanish language
    response = admin_client.post("/admin/languages/", json={"id": "es"})
    assert response.status_code == 200
    assert response.json() == {"id": "es"}
    assert admin_client.get("/languages/").json() == ["de", "en", "fr", "es"]
    # all texts now include spanish
    for milestone_group in admin_client.get("/admin/milestone-groups/").json():
        assert "es" in milestone_group["text"]
        for milestone in milestone_group["milestones"]:
            assert "es" in milestone["text"]
    for user_question in admin_client.get("/admin/user-questions/").json():
        assert "es" in user_question["text"]
    for child_question in admin_client.get("/admin/child-questions/").json():
        assert "es" in child_question["text"]


def test_post_delete_repost_language(admin_client: TestClient):
    assert admin_client.post("/admin/languages/", json={"id": "es"}).status_code == 200
    assert admin_client.get("/languages/").json() == ["de", "en", "fr", "es"]
    assert admin_client.delete("/admin/languages/es").status_code == 200
    assert admin_client.get("/languages/").json() == ["de", "en", "fr"]
    assert admin_client.post("/admin/languages/", json={"id": "es"}).status_code == 200
    assert admin_client.get("/languages/").json() == ["de", "en", "fr", "es"]


def test_post_language_invalid_already_exists(admin_client: TestClient):
    response = admin_client.post("/admin/languages/", json={"id": "de"})
    assert response.status_code == 400


def test_delete_language(admin_client: TestClient, static_dir: pathlib.Path):
    i18_json_path = static_dir / "i18n" / "fr.json"
    assert i18_json_path.is_file()
    # initially we have french versions of all texts
    for milestone_group in admin_client.get("/admin/milestone-groups/").json():
        assert "fr" in milestone_group["text"]
        for milestone in milestone_group["milestones"]:
            assert "fr" in milestone["text"]
    for user_question in admin_client.get("/admin/user-questions/").json():
        assert "fr" in user_question["text"]
    for child_question in admin_client.get("/admin/child-questions/").json():
        assert "fr" in child_question["text"]
    response = admin_client.delete("/admin/languages/fr")
    assert response.status_code == 200
    assert admin_client.get("/languages").json() == ["de", "en"]
    assert not i18_json_path.is_file()
    # no french texts
    for milestone_group in admin_client.get("/admin/milestone-groups/").json():
        assert "fr" not in milestone_group["text"]
        for milestone in milestone_group["milestones"]:
            assert "fr" not in milestone["text"]
    for user_question in admin_client.get("/admin/user-questions/").json():
        assert "fr" not in user_question["text"]
    for child_question in admin_client.get("/admin/child-questions/").json():
        assert "fr" not in child_question["text"]


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


def test_translate_non_admin_user(user_client: TestClient):
    response = user_client.post(
        "/admin/translate/",
        params={"text": "Meilenstein", "locale": "en", "source_lang": "DE"},
    )
    assert response.status_code == 401


class MockDeepLClient:
    def __init__(self, api_key):
        pass

    def translate_text(self, text, target_lang, source_lang, **kwargs):
        return type(
            "DeepLResponse",
            (),
            {"text": f"Mock translation of {text} from {source_lang} to {target_lang}"},
        )


@pytest.mark.parametrize("locale, deepl_locale", [("en", "EN-US"), ("fr", "FR")])
def test_translate(
    admin_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    locale: str,
    deepl_locale: str,
):
    text = "Meilenstein"
    monkeypatch.setattr("deepl.DeepLClient", MockDeepLClient)
    response = admin_client.post(
        "/admin/translate/", params={"text": text, "locale": locale}
    )
    assert response.status_code == 200
    assert response.json() == f"Mock translation of {text} from DE to {deepl_locale}"
