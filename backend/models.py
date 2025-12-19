from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, func

class Base(DeclarativeBase):
    pass

class Article(Base):
    __tablename__ = "wiki_article"

    id: Mapped[int] = mapped_column(primary_key=True)

    word: Mapped[str] = mapped_column(String(255), unique=True)
    word_slug: Mapped[str] = mapped_column(String(255), unique=True)
    clean_text: Mapped[str] = mapped_column(Text)

    summaries: Mapped[list["Summary"]] = relationship("Summary", back_populates="article", cascade="all, delete-orphan")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class Summary(Base):
    __tablename__ = "wiki_summary"

    id: Mapped[int] = mapped_column(primary_key=True)

    article_id: Mapped[int] = mapped_column(ForeignKey("wiki_article.id"), nullable=False)
    article: Mapped[Article] = relationship("Article", back_populates="summaries")

    word_count: Mapped[int] = mapped_column(Integer)
    summary_text: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    

