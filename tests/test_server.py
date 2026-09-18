import anthropic
import httpx2
import pytest
from fastapi.testclient import TestClient
from server import create_app

API_KEY = "test-key"
AUTH_HEADERS = {"X-API-Key": API_KEY}


class StubGraph:
    def invoke(self, state):
        return {**state, "answer": "final answer"}


class FailingGraph:
    def invoke(self, state):
        request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
        raise anthropic.APIConnectionError(request=request)


class AllowingModerator:
    def check(self, question):
        return True, ""


class BlockingModerator:
    def check(self, question):
        return False, "requests harmful content"


def test_query_returns_answer():
    app = create_app(StubGraph(), AllowingModerator(), api_key=API_KEY)
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"}, headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json()["answer"] == "final answer"


def test_query_returns_503_when_claude_api_unreachable():
    app = create_app(FailingGraph(), AllowingModerator(), api_key=API_KEY)
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"}, headers=AUTH_HEADERS)

    assert response.status_code == 503


def test_query_returns_400_when_blocked_by_moderator():
    app = create_app(StubGraph(), BlockingModerator(), api_key=API_KEY)
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"}, headers=AUTH_HEADERS)

    assert response.status_code == 400
    assert "requests harmful content" in response.json()["detail"]


def test_query_returns_401_when_api_key_missing():
    app = create_app(StubGraph(), AllowingModerator(), api_key=API_KEY)
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"})

    assert response.status_code == 401


def test_query_returns_401_when_api_key_wrong():
    app = create_app(StubGraph(), AllowingModerator(), api_key=API_KEY)
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"}, headers={"X-API-Key": "wrong"})

    assert response.status_code == 401


def test_query_returns_429_when_rate_limit_exceeded():
    app = create_app(StubGraph(), AllowingModerator(), api_key=API_KEY, rate_limit_per_minute=2)
    client = TestClient(app)

    client.post("/query", json={"question": "1"}, headers=AUTH_HEADERS)
    client.post("/query", json={"question": "2"}, headers=AUTH_HEADERS)
    response = client.post("/query", json={"question": "3"}, headers=AUTH_HEADERS)

    assert response.status_code == 429


def test_create_app_requires_api_key():
    with pytest.raises(ValueError):
        create_app(StubGraph(), AllowingModerator(), api_key="")
