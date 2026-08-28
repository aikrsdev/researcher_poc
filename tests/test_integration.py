from ollama import Client as OllamaClient
from fastapi.testclient import TestClient

from agents.researcher import Researcher
from agents.writer import Writer
from orchestrator import build_graph
from server import create_app


class FakeTavily:
    def search(self, query):
        return {"results": [{"url": "http://example.com", "content": "Example info"}]}


class FakeOllama:
    def chat(self, model, messages):
        return {"message": {"content": "final synthesized answer"}}


def test_full_pipeline_happy_path_with_real_graph_and_fake_clients():
    researcher = Researcher(FakeTavily(), FakeOllama(), "llama3.2")
    writer = Writer(FakeOllama(), "llama3.2")
    graph = build_graph(researcher, writer)
    app = create_app(graph, "http://localhost:11434")
    client = TestClient(app)

    response = client.post("/query", json={"question": "What is LangGraph?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "final synthesized answer"
    assert body["sources"] == ["http://example.com"]


def test_real_ollama_client_unreachable_returns_503():
    dead_url = "http://127.0.0.1:1"
    researcher = Researcher(FakeTavily(), OllamaClient(host=dead_url), "llama3.2")
    writer = Writer(OllamaClient(host=dead_url), "llama3.2")
    graph = build_graph(researcher, writer)
    app = create_app(graph, dead_url)
    client = TestClient(app)

    response = client.post("/query", json={"question": "What is LangGraph?"})

    assert response.status_code == 503
    assert dead_url in response.json()["detail"]
