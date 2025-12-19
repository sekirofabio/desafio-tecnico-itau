import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


import pytest

from schemas import WikiExtractorResult
from utils import wiki_extractor as wiki_extractor_module
from utils.wiki_extractor import WikipediaTextExtractor


@pytest.fixture
def fake_extractor_extract(monkeypatch):
    async def _fake_extract(self: WikipediaTextExtractor) -> WikiExtractorResult:
        return WikiExtractorResult(
            word=self.word,
            url="http://example.com/wiki/Test",
            summary="ok",
        )

    monkeypatch.setattr(WikipediaTextExtractor, "extract", _fake_extract)


@pytest.fixture
def fake_text_summarizer(monkeypatch):
    async def _fake_summarizer(text: str, word_count: int) -> str:
        return f"{word_count}:{text[:5]}"

    monkeypatch.setattr(wiki_extractor_module, "text_summarizer", _fake_summarizer)


@pytest.fixture
def fake_load_summary(monkeypatch):
    async def _fake_load_summary(self: WikipediaTextExtractor) -> None:
        self.summary_text = "summary"

    monkeypatch.setattr(WikipediaTextExtractor, "load_summary", _fake_load_summary)
