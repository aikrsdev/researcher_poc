# researcher_poc

A small research/Q&A pipeline built with two LangGraph agents and an
orchestrator:

- **Researcher** — searches the web (Tavily) for a given question and
  condenses the results into findings, using a local Ollama model.
- **Writer** — synthesizes the findings into a final answer.
- **Orchestrator** — a LangGraph `StateGraph` that runs the pipeline
  linearly: `researcher → writer`.

The pipeline is served over a small FastAPI app.

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com) running locally with the `llama3.2`
  model pulled (`ollama pull llama3.2`)
- A [Tavily](https://tavily.com) API key

## Configuration

Set these environment variables (a `.env` file works):

| Variable          | Default                   | Notes                    |
|-------------------|----------------------------|---------------------------|
| `OLLAMA_MODEL`     | `llama3.2`                 |                           |
| `OLLAMA_BASE_URL`  | `http://localhost:11434`   |                           |
| `TAVILY_API_KEY`   | —                           | Required, no default.    |

## Running

```bash
pip install -r requirements.txt
uvicorn server:app --reload
```

Then:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is LangGraph?"}'
```

## Design

See [`docs/superpowers/specs/2026-08-28-research-agent-orchestrator-design.md`](docs/superpowers/specs/2026-08-28-research-agent-orchestrator-design.md)
for the full design spec.

## Testing

```bash
pytest
```
