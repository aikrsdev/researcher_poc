import logging
import secrets
import time
from collections import defaultdict

import anthropic
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RATE_LIMIT_WINDOW_SECONDS = 60


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


def create_app(graph, moderator, api_key: str, rate_limit_per_minute: int = 20) -> FastAPI:
    if not api_key:
        raise ValueError("api_key must be a non-empty secret")

    app = FastAPI()
    request_log: dict[str, list[float]] = defaultdict(list)

    def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
        if not x_api_key or not secrets.compare_digest(x_api_key, api_key):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

    def enforce_rate_limit(request: Request) -> None:
        client_id = request.client.host if request.client else "unknown"
        now = time.monotonic()
        cutoff = now - RATE_LIMIT_WINDOW_SECONDS
        timestamps = request_log[client_id]
        timestamps[:] = [t for t in timestamps if t > cutoff]
        if len(timestamps) >= rate_limit_per_minute:
            logger.info("rate limit exceeded: client=%r", client_id)
            raise HTTPException(status_code=429, detail="Rate limit exceeded, try again later")
        timestamps.append(now)

    @app.post(
        "/query",
        response_model=QueryResponse,
        dependencies=[Depends(enforce_rate_limit), Depends(verify_api_key)],
    )
    def query(request: QueryRequest):
        logger.info("received query: question=%r", request.question)

        try:
            is_safe, reason = moderator.check(request.question)
            if not is_safe:
                logger.info("query blocked: reason=%r", reason)
                raise HTTPException(status_code=400, detail=f"Request blocked: {reason}")

            result = graph.invoke({"question": request.question, "findings": "", "answer": ""})
        except anthropic.AuthenticationError:
            logger.error("claude api authentication failed")
            raise HTTPException(status_code=500, detail="Claude API authentication failed — check ANTHROPIC_API_KEY")
        except anthropic.RateLimitError:
            logger.error("claude api rate limited")
            raise HTTPException(status_code=429, detail="Claude API rate limit exceeded")
        except anthropic.APIConnectionError:
            logger.error("claude api unreachable")
            raise HTTPException(status_code=503, detail="Claude API not reachable")
        except anthropic.APIStatusError as e:
            logger.error("claude api error: %s", e)
            raise HTTPException(status_code=502, detail=f"Claude API error: {e}")

        logger.info("query complete: answer=%d chars", len(result["answer"]))

        return QueryResponse(answer=result["answer"])

    return app


from config import load_settings  # noqa: E402
from agents.researcher import Researcher  # noqa: E402
from agents.writer import Writer  # noqa: E402
from agents.moderator import Moderator  # noqa: E402
from orchestrator import build_graph  # noqa: E402

_settings = load_settings()
_researcher = Researcher.from_config(_settings.claude_model)
_writer = Writer.from_config(_settings.claude_model)
_moderator = Moderator.from_config(_settings.claude_model)
_graph = build_graph(_researcher, _writer)
app = create_app(
    _graph,
    _moderator,
    api_key=_settings.api_key,
    rate_limit_per_minute=_settings.rate_limit_per_minute,
)
