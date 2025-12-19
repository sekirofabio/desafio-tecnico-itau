from typing import List

from fastapi import FastAPI, Depends
from fastapi import Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from dotenv import load_dotenv

from db import engine
from db import get_db

from models import Base
from models import Article
from models import Summary

from utils.wiki_extractor import normalize_word
from utils.wiki_extractor import WikipediaTextExtractor

from schemas import WikiExtractorResult
from schemas import WikiExtractorError
from schemas import WikiSavedWord
from schemas import WikiWordDatabase
from schemas import WikiSavedSummary
from schemas import WikiSummaryDatabase

app = FastAPI(title="Wikipedia Summarizer API")

load_dotenv()

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

@app.get("/health", summary="Health Test")
def health() -> dict:
    """
    Teste simples para verificar se a API está funcionando corretamente.
    """
    return {"status": "ok"}

@app.get(
    "/summarize", 
    response_model=WikiExtractorResult | WikiExtractorError, 
    summary="Gerar resumo do artigo da Wikipedia."
)
async def summarize(
    word: str = Query(description='Termo da Wikipedia'), 
    word_count: int =  Query(150, description='Número de palavras para o resumo do artigo.')
) -> WikiExtractorResult | WikiExtractorError:
    """
    Gera um resumo do artigo correspondente ao termo informado na Wikipédia.
    
    - **word**: termo da Wikipedia para o qual os resumos foram salvos.
    - **url**: url da página da Wikipedia.
    - **summary**: texto do resumo gerado.
    """

    extractor = WikipediaTextExtractor(word=word, word_count=word_count)

    result = await extractor.extract()

    return result.model_dump()

@app.get(
    "/summary/database", 
    response_model=WikiWordDatabase, 
    summary="Resumos da Wikipedia armazenados no banco de dados."
)
async def summary_database() -> WikiWordDatabase:
    """
    Retorna uma lista dos termos da Wikipedia com resumos salvos no banco de dados. 
    Um termos pode aparecer mais de uma vez se houver múltiplos resumos salvos para ele.
    
    - **word**: termo da Wikipedia para o qual os resumos foram salvos.
    - **word_count**: número de palavras para o resumo do artigo.
    - **created_at**: data e hora em que o resumo foi criado.
    """
    with Session(engine) as session:
        query = select(Summary).join(Summary.article).order_by(Article.word)
        summaries = session.scalars(query).all()

        saved_words: List[WikiSavedWord] = [
            WikiSavedWord(
                word=summary.article.word,
                word_count=summary.word_count,
                created_at=summary.created_at.isoformat()
            )
            for summary in summaries
        ]

    return WikiWordDatabase(summaries=saved_words)

@app.get(
    "/summary/database/{word}", 
    response_model=WikiSummaryDatabase | WikiExtractorError,
    summary="Recuperar resumos salvos anteriormente para um determinado termo."
)
async def summary_word_database(word: str) -> WikiSummaryDatabase:
    """
    Retorna uma lista com as informações dos resumos salvos anteriormente para um determinado termo.
    
    - **word**: termo da Wikipedia para o qual os resumos foram salvos.
    - **word_count**: número de palavras para o resumo do artigo.
    - **summary**: texto do resumo salvo.
    - **created_at**: data e hora em que o resumo foi criado.
    """
    with Session(engine) as session:
        query = select(Summary).join(Summary.article).where(Article.word == normalize_word(word)).order_by(Article.word)
        summaries = session.scalars(query).all()

        saved_summaries: List[WikiSavedSummary] = [
            WikiSavedSummary(
                word=summary.article.word,
                word_count=summary.word_count,
                summary=summary.summary_text,
                created_at=summary.created_at.isoformat()
            )
            for summary in summaries
        ]

    return WikiSummaryDatabase(summaries=saved_summaries)

