# researcher_poc

A small research/Q&A pipeline built with two LangGraph agents and an
orchestrator:

- **Moderator** — guardrail: classifies the question safe/unsafe via
  Claude before running the pipeline. Unsafe questions are rejected
  with `400` and never reach Researcher/Writer.
- **Researcher** — summarizes what it knows about a given question,
  using the Claude API (no web search).
- **Writer** — synthesizes the findings into a final answer.
- **Orchestrator** — a LangGraph `StateGraph` that runs the pipeline
  linearly: `researcher → writer`.

The pipeline is served over a small FastAPI app.

## Requirements

- Python 3.11+
- An Anthropic API key

## Configuration

| Variable                | Required | Default            |
|--------------------------|----------|---------------------|
| `ANTHROPIC_API_KEY`      | Yes      | —                   |
| `CLAUDE_MODEL`           | No       | `claude-haiku-4-5`  |
| `API_KEY`                | Yes      | —                   |
| `RATE_LIMIT_PER_MINUTE`  | No       | `20`                |

Copy `.env.example` to `.env` and fill in your key — `config.py` loads
it automatically (`.env` is gitignored, never committed).

`API_KEY` is a secret you choose (e.g. `python3 -c "import secrets;
print(secrets.token_urlsafe(32))"`) — clients must send it in an
`X-API-Key` header on every request to `/query`. Requests are also
rate-limited per client IP (`RATE_LIMIT_PER_MINUTE`, sliding 60s
window).

## Running

```bash
conda create -n researcher_poc python=3.11 -y
conda activate researcher_poc
pip install -r requirements.txt
cp .env.example .env  # then fill in ANTHROPIC_API_KEY
uvicorn server:app --reload
```

Then:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"question": "What is LangGraph?"}'
```

## Design

See [`docs/superpowers/specs/2026-08-28-research-agent-orchestrator-design.md`](docs/superpowers/specs/2026-08-28-research-agent-orchestrator-design.md)
for the full design spec.

## Testing

```bash
pytest
```
