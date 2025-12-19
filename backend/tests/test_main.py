from fastapi.testclient import TestClient

from main import app
from utils.wiki_extractor import WikipediaTextExtractor


def test_health_endpoint() -> None:
    client = TestClient(app)

    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_summarize_endpoint(fake_extractor_extract) -> None:
    client = TestClient(app)

    resp = client.get("/summarize", params={"word": "Test", "word_count": 10})

    assert resp.status_code == 200
    assert resp.json() == {
        "word": "Test",
        "url": "http://example.com/wiki/Test",
        "summary": "ok",
    }
