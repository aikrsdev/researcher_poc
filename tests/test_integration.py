from types import SimpleNamespace

import anthropic
from fastapi.testclient import TestClient

from agents.researcher import Researcher
from agents.writer import Writer
from agents.moderator import Moderator
from orchestrator import build_graph
from server import create_app


class FakeMessages:
    def create(self, model, max_tokens, messages):
        return SimpleNamespace(content=[SimpleNamespace(type="text", text="final synthesized answer")])


class FakeClaude:
    def __init__(self):
        self.messages = FakeMessages()


class AllowingModerator:
    def check(self, question):
        return True, ""


API_KEY = "test-key"
AUTH_HEADERS = {"X-API-Key": API_KEY}


def test_full_pipeline_happy_path_with_real_graph_and_fake_clients():
    researcher = Researcher(FakeClaude(), "claude-haiku-4-5")
    writer = Writer(FakeClaude(), "claude-haiku-4-5")
    graph = build_graph(researcher, writer)
    app = create_app(graph, AllowingModerator(), api_key=API_KEY)
    client = TestClient(app)

    response = client.post("/query", json={"question": "What is LangGraph?"}, headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert response.json()["answer"] == "final synthesized answer"


def test_real_claude_client_unreachable_returns_503():
    dead_client = anthropic.Anthropic(api_key="test-key", base_url="http://127.0.0.1:1", max_retries=0)
    researcher = Researcher(dead_client, "claude-haiku-4-5")
    writer = Writer(dead_client, "claude-haiku-4-5")
    moderator = Moderator(dead_client, "claude-haiku-4-5")
    graph = build_graph(researcher, writer)
    app = create_app(graph, moderator, api_key=API_KEY)
    client = TestClient(app)

    response = client.post("/query", json={"question": "What is LangGraph?"}, headers=AUTH_HEADERS)

    assert response.status_code == 503
