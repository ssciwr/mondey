import pandas as pd
import pytest
from fastapi.testclient import TestClient

from mondey_backend.import_data.manager.data_manager import DataManager
from mondey_backend.import_data.manager.import_manager import ImportManager


def csv_upload() -> tuple[str, bytes, str]:
    csv = pd.DataFrame({"CASE": [999], "FK05": [1]}).to_csv(sep="\t", index=False)
    return "data.csv", csv.encode("utf-16"), "text/csv"


def test_import_csv_with_researcher_code(admin_client: TestClient, monkeypatch):
    imported_research_group_id = None

    async def run_import(manager: ImportManager) -> int:
        nonlocal imported_research_group_id
        imported_research_group_id = manager.research_group_id
        return 1

    async def save_csv(*args, **kwargs) -> None:
        pass

    monkeypatch.setattr(ImportManager, "run_additional_data_import", run_import)
    monkeypatch.setattr(
        DataManager, "save_additional_import_csv_into_dataframe", save_csv
    )

    response = admin_client.post(
        "/admin/research/import-csv/",
        files={"additional_data_file": csv_upload()},
        data={"research_group_id": "123451"},
    )

    assert response.status_code == 200
    assert response.json()["children_imported"] == 1
    assert imported_research_group_id == 123451


def test_import_csv_rejects_invalid_researcher_code(admin_client: TestClient):
    response = admin_client.post(
        "/admin/research/import-csv/",
        files={"additional_data_file": csv_upload()},
        data={"research_group_id": "703207"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid researcher code"


@pytest.mark.asyncio
async def test_import_manager_applies_researcher_code():
    class UserSession:
        user = None

        def add(self, user) -> None:
            self.user = user

        async def flush(self) -> None:
            pass

    user_session = UserSession()
    manager = ImportManager(
        session=None,
        user_session=user_session,  # type: ignore[arg-type]
        research_group_id=123451,
    )

    parent = await manager.create_parent_for_child(999)

    assert parent.research_group_id == 123451
    assert user_session.user is parent
