import pytest

from utils import summarizer


@pytest.mark.asyncio
async def test_text_summarizer_uses_chain(monkeypatch) -> None:
    class DummyResponse:
        content = "summary"

    class DummyChain:
        last_payload: dict | None = None

        async def ainvoke(self, payload: dict) -> DummyResponse:
            DummyChain.last_payload = payload
            return DummyResponse()

    class DummyPrompt:
        def __init__(self, template: str, input_variables: list[str]) -> None:
            self.template = template
            self.input_variables = input_variables

        def __or__(self, llm: object) -> DummyChain:
            return DummyChain()

    class DummyLLM:
        def __init__(self, model: str, temperature: int) -> None:
            self.model = model
            self.temperature = temperature

    monkeypatch.setattr(summarizer, "PromptTemplate", DummyPrompt)
    monkeypatch.setattr(summarizer, "ChatOpenAI", DummyLLM)

    result = await summarizer.text_summarizer("Hello world", word_count=5)

    assert result == "summary"
    assert DummyChain.last_payload == {
        "original_text": "Hello world",
        "word_count": 5,
    }
