import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


def create_app(graph, ollama_base_url: str) -> FastAPI:
    app = FastAPI()

    @app.post("/query", response_model=QueryResponse)
    def query(request: QueryRequest):
        try:
            result = graph.invoke(
                {"question": request.question, "search_results": [], "findings": "", "answer": ""}
            )
        except (ConnectionError, httpx.ConnectError, httpx.TimeoutException):
            raise HTTPException(
                status_code=503,
                detail=f"Ollama not reachable at {ollama_base_url}",
            )

        sources = [r["url"] for r in result.get("search_results", []) if r.get("url")]
        return QueryResponse(answer=result["answer"], sources=sources)

    return app


from config import load_settings, validate  # noqa: E402
from agents.researcher import Researcher  # noqa: E402
from agents.writer import Writer  # noqa: E402
from orchestrator import build_graph  # noqa: E402

_settings = load_settings()
validate(_settings)
_researcher = Researcher.from_config(_settings.tavily_api_key, _settings.ollama_base_url, _settings.ollama_model)
_writer = Writer.from_config(_settings.ollama_base_url, _settings.ollama_model)
_graph = build_graph(_researcher, _writer)
app = create_app(_graph, _settings.ollama_base_url)
