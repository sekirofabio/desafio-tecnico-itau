from pydantic import BaseModel

class WikiExtractorResult(BaseModel):
    word: str
    url: str
    summary: str