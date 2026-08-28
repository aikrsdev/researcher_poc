import anthropic
import httpx2
from fastapi.testclient import TestClient
from server import create_app


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
    app = create_app(StubGraph(), AllowingModerator())
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"})

    assert response.status_code == 200
    assert response.json()["answer"] == "final answer"


def test_query_returns_503_when_claude_api_unreachable():
    app = create_app(FailingGraph(), AllowingModerator())
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"})

    assert response.status_code == 503


def test_query_returns_400_when_blocked_by_moderator():
    app = create_app(StubGraph(), BlockingModerator())
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"})

    assert response.status_code == 400
    assert "requests harmful content" in response.json()["detail"]
