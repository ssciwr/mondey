import asyncio
import json
import zlib

import pytest
from fastapi.testclient import TestClient

from mondey_backend import statistics


def research_data(client: TestClient) -> list[dict]:
    response = client.get("/research/data/")
    assert response.status_code == 200
    events = [json.loads(line) for line in response.iter_lines()]
    assert events[-1]["type"] == "data"
    return events[-1]["data"]


def test_research_data_invalid_user(user_client: TestClient):
    response = user_client.get("/research/data/")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "client_fixture", ["research_client", "research_client_full_data_access"]
)
def test_research_data_stream(request, client_fixture):
    client = request.getfixturevalue(client_fixture)
    response = client.get("/research/data/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/jsonl")
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-accel-buffering"] == "no"
    events = [json.loads(line) for line in response.iter_lines()]
    assert events[:-1] == [
        {"type": "progress", "stage": stage}
        for stage in [
            "checkingAccess",
            "answerSessions",
            "milestoneAnswers",
            "childAges",
            "userAnswers",
            "childAnswers",
            "researchGroups",
            "assembling",
            "transferring",
        ]
    ]
    assert events[-1]["type"] == "data"


def test_research_data_stream_failure(research_client: TestClient, monkeypatch):
    def fail(*args):
        raise RuntimeError("Private database details")

    monkeypatch.setattr("mondey_backend.statistics.get_milestone_answers", fail)
    response = research_client.get("/research/data/")
    events = [json.loads(line) for line in response.iter_lines()]
    assert events[0]["type"] == "progress"
    assert events[-1] == {"type": "error"}
    assert not any(event["type"] == "data" for event in events)
    assert "Private database details" not in response.text


@pytest.mark.asyncio
async def test_research_progress_delivered_before_work_even_with_gzip(
    research_client: TestClient, monkeypatch
):
    # TestClient buffers responses, so observe ASGI sends directly to ensure
    # neither the endpoint nor compression holds progress until extraction ends.
    events: list[dict] = []
    pending = b""
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    original_get_test_ids = statistics.get_test_account_user_ids
    original_get_answers = statistics.get_milestone_answers

    async def get_test_ids(user_session):
        assert events[-1]["stage"] == "checkingAccess"
        return await original_get_test_ids(user_session)

    def get_answers(session):
        assert events[-1]["stage"] == "milestoneAnswers"
        return original_get_answers(session)

    monkeypatch.setattr(statistics, "get_test_account_user_ids", get_test_ids)
    monkeypatch.setattr(statistics, "get_milestone_answers", get_answers)

    async def send(message):
        nonlocal pending
        if message["type"] == "http.response.start":
            assert (b"content-encoding", b"gzip") in message["headers"]
        elif message["type"] == "http.response.body":
            pending += decoder.decompress(message.get("body", b""))
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                events.append(json.loads(line))

    async def receive():
        await asyncio.Event().wait()

    await asyncio.wait_for(
        research_client.app(
            {
                "type": "http",
                "asgi": {"version": "3.0", "spec_version": "2.4"},
                "http_version": "1.1",
                "method": "GET",
                "scheme": "http",
                "path": "/research/data/",
                "query_string": b"",
                "root_path": "",
                "headers": [(b"accept-encoding", b"gzip")],
            },
            receive,
            send,
        ),
        timeout=5,
    )
    assert len(events) == 10
    assert events[-1]["type"] == "data"
    assert len(events[-1]["data"]) == 3


def test_research_data(research_client: TestClient):
    data = research_data(research_client)
    # only answer sessions from children of users in the same research group should be included
    # i.e. children of users 2 & 3 with research group id 123451
    # i.e. children with ids 1 & 2
    # i.e. answer sessions with ids 1, 2 & 4, which contain answers for milestones 1 & 2
    assert len(data) == 3
    for item in data:
        assert item["research_group_id"] == 123451
        assert item["user_question_1"] == "lorem ipsum"
        # for user question 2, the answer is "other" which is the additional_option for this question,
        # so we get the additional_answer here instead of the answer:
        assert item["user_question_2"] == "dolor sit"
        assert item["child_question_1"] == "a"
        assert item["child_question_2"] == "apple"
        assert "milestone_id_1" in item
        assert "milestone_id_2" in item


def test_research_data_full_data_access(research_client_full_data_access: TestClient):
    data = research_data(research_client_full_data_access)
    # all completed answer sessions (excluding those from test users) are included
    assert len(data) == 4
    assert [item["research_group_id"] for item in data].count(123451) == 3
    assert [item["research_group_id"] for item in data].count(0) == 1


def test_research_data_deleted_child(admin_client: TestClient):
    # admin client has 1 child, sees all 4 completed answer sessions:
    assert len(admin_client.get("/users/children/").json()) == 1
    assert len(research_data(admin_client)) == 4
    # if a child is deleted, their answers are no longer included: child 3 had 1 completed answer session
    assert admin_client.delete("/users/children/3?dry_run=false").status_code == 200
    assert len(admin_client.get("/users/children/").json()) == 0
    assert len(research_data(admin_client)) == 3


def test_research_data_admin_suspicious_excluded(admin_client: TestClient):
    # admin client has 1 child, sees all 4 completed answer sessions:
    assert len(admin_client.get("/users/children/").json()) == 1
    assert len(research_data(admin_client)) == 4
    # if an answer session is marked as suspicious by an admin, it is excluded from research data:
    assert (
        admin_client.post(
            "/admin/milestone-answer-sessions/1?suspicious=true"
        ).status_code
        == 200
    )
    assert len(research_data(admin_client)) == 3
    assert (
        admin_client.post(
            "/admin/milestone-answer-sessions/2?suspicious=true"
        ).status_code
        == 200
    )
    assert len(research_data(admin_client)) == 2
    # if the suspicious flag is removed, the answer session is included again:
    assert (
        admin_client.post(
            "/admin/milestone-answer-sessions/1?suspicious=false"
        ).status_code
        == 200
    )
    assert len(research_data(admin_client)) == 3
    assert (
        admin_client.post(
            "/admin/milestone-answer-sessions/2?suspicious=false"
        ).status_code
        == 200
    )
    assert len(research_data(admin_client)) == 4


def test_research_names(research_client: TestClient):
    response = research_client.get("/research/names/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert "milestone" in data
    assert "milestone_label" in data
    assert "user_question" in data
    assert "child_question" in data
    assert len(data["milestone"]) == 5
    assert data["milestone"]["1"] == "m1"
    assert data["milestone"]["5"] == "m5"
    assert data["milestone_label"]["1"] == "m1 :: g1_de_t :: m1_de_t"
    assert data["milestone_label"]["5"] == "m5 :: g1_de_t :: m5_de_t"
    assert len(data["user_question"]) == 3
    assert data["user_question"]["1"] == "User Question 1"
    assert data["user_question"]["2"] == "User Question 2"
    assert len(data["child_question"]) == 3
    assert data["child_question"]["1"] == "Child Question 1"
    assert data["child_question"]["2"] == "Child Question 2"


def test_research_names_language(research_client: TestClient):
    response = research_client.get("/research/names/?lang_id=en")
    assert response.status_code == 200
    assert response.json()["milestone_label"]["1"] == "m1 :: g1_en_t :: m1_en_t"
