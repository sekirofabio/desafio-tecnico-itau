import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from db import engine
from main import app
from models import Base
from utils.summarizer import text_summarizer
from utils.wiki_extractor import WikipediaTextExtractor


def _ensure_integration_enabled() -> None:
    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Set RUN_INTEGRATION=1 to run integration tests.")


def _require_env(*keys: str) -> None:
    missing = [key for key in keys if not os.getenv(key)]
    if missing:
        pytest.skip(f"Missing env vars for integration tests: {', '.join(missing)}")


def _ensure_db_ready() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - env dependent
        pytest.skip(f"Database not available for integration tests: {exc}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_text_summarizer_integration() -> None:
    _ensure_integration_enabled()
    _require_env("OPENAI_API_KEY")

    result = await text_summarizer("Python e uma linguagem popular.", word_count=10)

    assert isinstance(result, str)
    assert result.strip()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_wiki_extractor_integration() -> None:
    _ensure_integration_enabled()
    _require_env("OPENAI_API_KEY", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_HOST")
    _ensure_db_ready()

    extractor = WikipediaTextExtractor(word="Python", word_count=30)
    result = await extractor.extract()

    assert result.word.lower() == "python"
    assert result.url.startswith("https://pt.wikipedia.org/wiki/")
    assert result.summary.strip()


@pytest.mark.integration
def test_summarize_endpoint_integration() -> None:
    _ensure_integration_enabled()
    _require_env("OPENAI_API_KEY", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_HOST")
    _ensure_db_ready()

    client = TestClient(app)
    resp = client.get("/summarize", params={"word": "Python", "word_count": 20})

    assert resp.status_code == 200
    data = resp.json()
    assert data["word"].lower() == "python"
    assert data["url"].startswith("https://pt.wikipedia.org/wiki/")
    assert data["summary"].strip()
