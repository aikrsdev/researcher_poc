from fastapi.testclient import TestClient
from server import create_app


class StubGraph:
    def invoke(self, state):
        return {**state, "answer": "final answer", "search_results": [{"url": "http://example.com"}]}


class FailingGraph:
    def invoke(self, state):
        raise ConnectionError("connection refused")


def test_query_returns_answer_and_sources():
    app = create_app(StubGraph(), "http://localhost:11434")
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "final answer"
    assert body["sources"] == ["http://example.com"]


def test_query_returns_503_when_ollama_unreachable():
    app = create_app(FailingGraph(), "http://localhost:11434")
    client = TestClient(app)

    response = client.post("/query", json={"question": "test?"})

    assert response.status_code == 503
    assert "http://localhost:11434" in response.json()["detail"]
