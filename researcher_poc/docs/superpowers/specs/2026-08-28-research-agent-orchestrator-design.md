# Research Agent Orchestrator — Design

## Purpose

A research/Q&A pipeline: a user submits a question via an API, a
researcher agent gathers information from the web, and a writer agent
synthesizes it into a final answer.

## Stack

- Python
- LangGraph for orchestration
- FastAPI for the API layer
- Ollama (local) running `llama3.2` as the LLM backend
- Tavily for web search

## Architecture

```
Client → FastAPI (POST /query) → LangGraph orchestrator
                                     ├─ researcher node → Tavily search → llama3.2 (summarize)
                                     └─ writer node → llama3.2 (synthesize final answer)
                                     → END → JSON response
```

Modules:

- `agents/researcher.py` — researcher node
- `agents/writer.py` — writer node
- `orchestrator.py` — LangGraph `StateGraph` wiring
- `server.py` — FastAPI app, single endpoint
- `config.py` — env var loading (`OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `TAVILY_API_KEY`)

## Data Flow

Shared graph state:

```python
class GraphState(TypedDict):
    question: str
    search_results: list[dict]   # raw Tavily hits
    findings: str                # researcher's summarized notes (with source URLs)
    answer: str                  # writer's final output
```

Graph edges: `START → researcher → writer → END`. No conditionals, no
loops — a fixed linear pipeline.

- **Researcher node**: calls Tavily with `question`, gets raw hits,
  then makes one llama3.2 call to condense them into `findings`
  (plain text, source URLs retained).
- **Writer node**: prompts llama3.2 with `question` + `findings`,
  produces `answer`.

Both nodes are plain functions wrapping a direct Ollama client call —
no LangChain agent executors or tool-calling loops, since the flow is
fixed and the model never needs to decide whether to search.

## API

`POST /query`

Request: `{"question": "<string>"}`

Response: `{"answer": "<string>", "sources": ["<url>", ...]}`

## Error Handling

- Tavily request fails or times out → researcher catches it, sets
  `findings` to a note that search failed; the writer still runs
  (degrades to model-knowledge-only answer) rather than failing the
  whole request.
- Ollama unreachable → raised as a clear exception, caught at the
  FastAPI layer, returned as HTTP 503 with a message naming
  `OLLAMA_BASE_URL`.
- Missing `TAVILY_API_KEY` → fail fast at process startup, not
  per-request.

## Testing

- `pytest` unit tests per node, with Tavily and Ollama calls mocked —
  verify state transformations (e.g., researcher populates `findings`
  from a stubbed search response).
- One graph-wiring test with both nodes stubbed, asserting edges fire
  in order (`researcher` before `writer`).
- No live-API tests by default (would require a running local Ollama
  instance and a real Tavily key). A manual smoke-test procedure will
  be documented in the README for exercising the real pipeline
  end-to-end.

## Configuration Defaults

- `OLLAMA_MODEL=llama3.2`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `TAVILY_API_KEY` — required, no default
