import pytest

from schemas import WikiExtractorResult
from utils.wiki_extractor import WikipediaPageNotFoundError, WikipediaTextExtractor


def test_normalize_word_handles_stopwords() -> None:
    extractor = WikipediaTextExtractor("Casa de Papel")

    assert extractor.wiki_word == "Casa_de_Papel"


def test_text_cleaner_extracts_text() -> None:
    extractor = WikipediaTextExtractor("Teste")
    extractor.raw_text = """
    <html>
      <body>
        <div id="mw-content-text">
          <p>First line.</p>
          <script>ignore me</script>
          <p>Second line.</p>
        </div>
      </body>
    </html>
    """

    extractor.text_cleaner()

    assert "First line." in extractor.clean_text
    assert "Second line." in extractor.clean_text
    assert "ignore me" not in extractor.clean_text


def test_text_cleaner_raises_on_missing_article() -> None:
    extractor = WikipediaTextExtractor("Nada")
    extractor.raw_text = '<div class="noarticletext">missing</div>'

    with pytest.raises(WikipediaPageNotFoundError):
        extractor.text_cleaner()


@pytest.mark.asyncio
async def test_text_summary_awaits_summarizer(fake_text_summarizer) -> None:
    extractor = WikipediaTextExtractor("Teste", word_count=3)
    extractor.clean_text = "Hello world"

    await extractor.text_summary()

    assert extractor.summary_text == "3:Hello"


@pytest.mark.asyncio
async def test_extract_returns_schema(fake_load_summary) -> None:
    extractor = WikipediaTextExtractor("Teste")
    result = await extractor.extract()

    assert isinstance(result, WikiExtractorResult)
    assert result.word == "Teste"
    assert result.summary == "summary"
