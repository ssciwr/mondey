from fastapi.testclient import TestClient


def test_create_documents_invalid(admin_client: TestClient):
    # text file instead of pdf
    files = {"file": ("test.txt", b"this is a test", "text/plain")}
    form_data = {"title": "Test title", "description": "Test description."}
    res_admin = admin_client.post("/admin/documents/", data=form_data, files=files)
    assert res_admin.status_code == 400
    assert "pdf" in res_admin.json()["detail"].lower()


def test_create_documents(admin_client: TestClient):
    files = {"file": ("test.pdf", b"%PDF-1.1\n", "application/pdf")}
    form_data = {"title": "Test title", "description": "Test description."}

    # create a document
    res_admin = admin_client.post("/admin/documents/", data=form_data, files=files)
    assert res_admin.status_code == 200

    res_user = admin_client.get("/documents/")
    assert res_user.status_code == 200
    docs = res_user.json()
    assert len(docs) == 1
    assert docs[0]["id"] == 1
    assert docs[0]["title"] == "Test title"
    assert docs[0]["description"] == "Test description."
    assert docs[0]["filename"] == "test.pdf"
    assert docs[0]["uploaded_by_user_id"] == 1

    # modify a document
    docs[0]["title"] = "Updated title"
    docs[0]["description"] = "Updated description."
    res_admin = admin_client.put("/admin/documents/1", json=docs[0])
    assert res_admin.status_code == 200

    res_user = admin_client.get("/documents/")
    assert res_user.status_code == 200
    docs = res_user.json()
    assert len(docs) == 1
    assert docs[0]["id"] == 1
    assert docs[0]["title"] == "Updated title"
    assert docs[0]["description"] == "Updated description."
    assert docs[0]["filename"] == "test.pdf"
    assert docs[0]["uploaded_by_user_id"] == 1

    # delete a document
    res_admin = admin_client.delete("/admin/documents/1")
    assert res_admin.status_code == 200

    res_user = admin_client.get("/documents/")
    assert res_user.status_code == 200
    assert len(res_user.json()) == 0
