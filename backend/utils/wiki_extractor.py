from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

import re
from urllib.parse import unquote
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Session

from db import engine

from models import Article, Summary

from schemas import WikiExtractorResult
from schemas import WikiExtractorError

from utils.summarizer import text_summarizer

STOPWORDS = ["de", "da", "do", "das", "dos", "e", "em", "para", "por", "com"]

class WikipediaPageNotFoundError(Exception):
    """
    Raised when the Wikipedia page for a given word does not exist.
    """

def normalize_word(word: str) -> str:
    word = word and word.strip() or ''
    base = re.sub(r"\s+", " ", word)

    words = base.split(" ")
    normalized_words: list[str] = []

    for word in words:
        lower = word.lower()

        if lower in STOPWORDS:
            normalized_words.append(lower)
        else:
            normalized_words.append(lower.capitalize())

    return '_'.join(normalized_words)

def format_url(word: str) -> str:
    wiki_word = normalize_word(word)

    return f"https://pt.wikipedia.org/wiki/{quote(wiki_word, safe=':_()')}"

class WikipediaTextExtractor:
    def __init__(self, word: str, word_count: int = 150) -> None:
        self.word = word and word.strip() or ''
        self.word_count = word_count
        self.raw_text = ''
        self.clean_text = ''
        self.summary_text = ''
        self.wiki_word = normalize_word(self.word)
        self.article = None
        self.article_id = None
        self.summary = None

        self.url = format_url(self.word)

    def fecth_article(self) -> None:
        session = requests.Session()
        headers: dict = {
            "User-Agent": "Mozilla/5.0 (compatible; WikipediaFetcher/1.0; +https://example.com)",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        }

        resp = session.get(self.url, headers=headers, timeout=15.0, allow_redirects=True)
        if resp.status_code == 404:
            raise WikipediaPageNotFoundError(f'Wikipedia page not found for "{self.word}": {self.url}')

        resp.raise_for_status()

        self.raw_text = resp.text

    def text_cleaner(self) -> None:
        soup = BeautifulSoup(self.raw_text, "html.parser")

        if soup.select_one("div.noarticletext"):
            raise WikipediaPageNotFoundError(f'Wikipedia page not found for "{self.word}"')

        content = soup.select_one("div#mw-content-text") or soup

        for tag in content.select(
            "script, style, noscript, svg, img, figure, table, "
            "div.navbox, div.infobox, div.metadata, div.reflist, "
            "ol.references, sup.reference, span.mw-editsection"
        ):
            tag.decompose()

        text = content.get_text(separator="\n", strip=True)

        lines = [ln.strip() for ln in text.splitlines()]
        cleaned_lines = []
        last_blank = False
        for ln in lines:
            if not ln:
                if not last_blank:
                    cleaned_lines.append("")
                last_blank = True
            else:
                cleaned_lines.append(ln)
                last_blank = False
        
        self.clean_text = "\n".join(cleaned_lines).strip()

        if not self.clean_text:
            raise WikipediaPageNotFoundError(f'No extractable text found for "{self.word}"')
        
    async def text_summary(self) -> None:
        summary = await text_summarizer(self.clean_text, word_count=self.word_count)

        self.summary_text = summary

    async def extract_from_wikipedia(self) -> None:
        self.fecth_article()
        self.text_cleaner()
        self.save_article()

        await self.text_summary()
        self.save_summary()

    async def load_summary(self) -> None:
        if not self.wiki_word:
            return
        
        word_slug = self.wiki_word.strip().lower()

        with Session(engine) as session:
            article = session.scalar(
                select(Article).where(Article.word_slug == word_slug)
            )

            summary = article and session.scalar(
                select(Summary).where(Summary.article_id == article.id, Summary.word_count == self.word_count)
            )

        self.article = article
        self.summary = summary
        self.article_id = article.id if article else None

        if not self.article:
            print('Load from Wikipedia.')
            await self.extract_from_wikipedia()
        elif self.summary:
            print('Load from database.')
            self.summary_text = self.summary.summary_text
        else:
            print('Generate new summary.')

            self.clean_text = self.article.clean_text

            await self.text_summary()
            self.save_summary()

    def save_article(self) -> None:
        with Session(engine) as session:
            if not self.wiki_word:
                return
            
            word_slug = self.wiki_word.strip().lower()
            
            article = Article(
                word=self.wiki_word,
                word_slug=word_slug,
                clean_text=self.clean_text
            )

            session.add(article)
            session.commit()
            session.refresh(article)

        self.article = article
        self.article_id = article.id

    def save_summary(self) -> None:
        with Session(engine) as session:
            if not self.article_id:
                return
            
            summary = Summary(
                article_id=self.article_id,
                word_count=self.word_count,
                summary_text=self.summary_text
            )

            session.add(summary)
            session.commit()

        self.summary = summary
    
    async def extract(self) -> WikiExtractorResult | WikiExtractorError:
        try:
            await self.load_summary()
        except WikipediaPageNotFoundError as e:
            return WikiExtractorError(
                word=self.word,
                url=self.url,
                message='Página da Wikipedia não encontrada para o termo solicitado.'
            )

        return WikiExtractorResult(
            word=self.word,
            url=self.url,
            summary=self.summary_text
        )
