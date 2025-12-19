from pydantic import BaseModel

class WikiExtractorResult(BaseModel):
    word: str
    url: str
    summary: str

class WikiExtractorError(BaseModel):
    word: str
    url: str
    message: str

class WikiSavedWord(BaseModel):
    word: str
    word_count: int
    created_at: str

class WikiWordDatabase(BaseModel):
    summaries: list[WikiSavedWord]

class WikiSavedSummary(BaseModel):
    word: str
    word_count: int
    summary: str
    created_at: str

class WikiSummaryDatabase(BaseModel):
    summaries: list[WikiSavedSummary]